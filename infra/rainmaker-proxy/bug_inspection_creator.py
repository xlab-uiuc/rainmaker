import csv
import os
import json
import pandas as pd
import re
from utils import get_index_of_closing_bracket


def generate_reproduction_file(output_dir_path, output_dir_proj, alarm_file, stat_round_dir, calibrate_stat_dir):
    bug_f_path = os.path.join(output_dir_path, "bug_inspection.csv")
    boring_f_path = os.path.join(output_dir_path, "boring_failures.csv")
    f = open(bug_f_path, "w", encoding="utf-8")
    bf = open(boring_f_path, "w", encoding="utf-8")
    f.write("name\tturn\tURI\tSDK\tpolicy\toutcome\ttime\texcp_type\theuristic1\theuristic2\tbug?\tbug_ID\tbug_link\n")
    bf.write("name\tturn\tURI\tSDK\tpolicy\toutcome\ttime\texcp_type\theuristic1\theuristic2\tbug?\tbug_ID\tbug_link\n")
    with open(alarm_file, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        marked_test_set = set()
        test_injection_failure = 0
        src_injection_failure = 0
        for row in rows:
            # print("Row from alarm file:")
            # print(row)
            # print(row['name'], row['policy'], row['round'])
            test_name = row['name']
            test_turn = row['round']
            req_f_path, overview_f_path, marked_test, inject_round_num, collect_round_num = locate_files_path(
                stat_round_dir, calibrate_stat_dir, test_name, test_turn)

            # Test is marked when the number of injection points is not equal to the expected.
            if marked_test != "":
                marked_test_set.add((test_name, inject_round_num, collect_round_num))
            injected_request, sdk_api = find_injected_req_and_sdk_api(req_f_path)
            if "Cannot find injected request" in injected_request:
                continue
            policy = row['policy']
            outcome = row['outcome']
            boring = row['boring_failure']
            run_time = find_run_time(overview_f_path)
            excp_type = find_excp_type(row['message'])
            heur_1 = selected_by_heuristic_1(row['fail_in_test'])
            heur_2 = selected_by_heuristic_2(row['boring_failure'])

            if boring == "True":
                bf.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    test_name, test_turn, injected_request, sdk_api, policy, outcome, run_time, excp_type, heur_1,
                    heur_2))
            else:
                # print("Exception type: %s" % excp_type)
                if "test" in sdk_api and excp_type != "Assertion":
                    test_injection_failure += 1
                    continue
                src_injection_failure += 1
                f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n"
                        .format(test_name, test_turn, injected_request, sdk_api,
                                policy, outcome, run_time, excp_type, heur_1, heur_2))
    f.close()
    bf.close()

    if_dir_exist = os.path.isdir(output_dir_proj)
    if not if_dir_exist:
        os.makedirs(output_dir_proj)

    # Put the file under full collection folder
    df_bug = pd.read_csv(bug_f_path, sep='\t')
    df_boring = pd.read_csv(boring_f_path, sep='\t')
    df_bug.to_csv(os.path.join(output_dir_proj, "bug_inspection.csv"), sep='\t', index=False)
    df_boring.to_csv(os.path.join(output_dir_proj, "boring_failures.csv"), sep='\t', index=False)

    print("#######################################")
    print("Number of tests that has inconsistent round number: {}".format(len(marked_test_set)))
    for ele in marked_test_set:
        print("{}; Actual injection #: {}; Expected injection #: {}".format(ele[0], ele[1], ele[2]))
    print("#######################################")
    print("Number of injections on test code: {}".format(test_injection_failure))
    print("Number of injections on source code: {}".format(src_injection_failure))
    print("We prune out injections on test code")
    print("Total failed tests in the bug_inspection: {}".format(src_injection_failure))
    # There are xlocation header with empty values => lead to inconsistent round number
    # print("{}\ntest that has inconsistent round number {}".format(marked_test_set, len(marked_test_set)))


def detect_boring_failure(boring):
    return True if boring.strip() == "True" else "False"


def selected_by_heuristic_1(fail_in_test):
    return "False" if fail_in_test.strip() == "True" else "True"


def selected_by_heuristic_2(boring_failure):
    return "False" if boring_failure.strip() == "True" else "True"


def find_excp_type(plain_message):
    exception_type = "Cannot find exception type"
    if "Assert." in plain_message or \
        "Expected: " in plain_message or \
        "Expected (" in plain_message:
        exception_type = "Assertion"
    elif "Exception :" in plain_message:
        exception_type = plain_message.split(" :")[0]
    elif "Exception:" in plain_message:
        # print(plain_message)
        exception_type = plain_message.split("Exception:")[0].split(". ")[-1]
    return exception_type


def locate_files_path(stat_dir, collection_stat_dir, test_name, injection_round):
    inject_round_num = 0
    inject_test_path = os.path.join(stat_dir, test_name)
    for f in os.listdir(inject_test_path):
        child = os.path.join(inject_test_path, f)
        if os.path.isdir(child):
            inject_round_num += 1
    collect_round_sdk_path = os.path.join(collection_stat_dir, test_name, '0', 'CALLSITE.csv')
    print(collect_round_sdk_path)
    try:
        collect_round_num = len(pd.read_csv(collect_round_sdk_path, sep='\t', header=None).index)
    except FileNotFoundError as e:
        print("Cannot find reference round CALLSITE.csv file!")
        collect_round_num = inject_round_num

    if inject_round_num != collect_round_num:
        marked_test = test_name
    else:
        marked_test = ""

    turn_dir = os.path.join(stat_dir, test_name, injection_round)
    req_f_path = os.path.join(turn_dir, "request.json")
    overview_f_path = os.path.join(turn_dir, "overview.txt")
    return req_f_path, overview_f_path, marked_test, inject_round_num, collect_round_num


def find_injected_req_and_sdk_api(request_file):
    # print(request_file)
    req_file = open(request_file)
    is_put = True
    if is_put:
        json_string = req_file.readlines()[0]
        pattern = '^\[\]'
        result = re.match(pattern, json_string)
        if result:
            req_file.close()

        index_cb = get_index_of_closing_bracket(json_string, 0)
        json_string = json_string[:index_cb + 1]
        reqs = json.loads(json_string)
    else:
        reqs = json.load(req_file)

    # reqs = json.load(req_file)
    uri = "Injected request NOT found."
    sdk_api = "SDK API NOT found."
    for request in reqs:
        http_request = request['httpRequest']
        http_response = request['httpResponse']
        if "headers" not in http_response:
            continue

        if "injected" in http_response['headers']:
            host = str(http_request['headers']['Host'][0])
            http_method = str(http_request['method'])
            http_path = str(http_request['path'])
            query_string = ""
            if "queryStringParameters" in http_request:
                query_string = "/"
                for key, value in http_request['queryStringParameters'].items():
                    # print(key, value)
                    query_string += key + "=" + value[0]
            uri = host + http_method + http_path + query_string

            if "x-location" in http_request['headers']:
                x_location = http_request['headers']['x-location'][0]
                sdk_api = x_location
                # if "#" in x_location:
                #     sdk_api = x_location.split("#")[-1]
                # else:
                #     sdk_api = x_location
            req_file.close()
            return uri, sdk_api
        else:
            continue
    req_file.close()
    return uri, sdk_api


def find_run_time(overview_file_path):
    overview_file = open(overview_file_path)
    run_time = "Running time NOT found."
    lines = overview_file.readlines()
    for line in lines:
        if line.startswith("Running time"):
            run_time = line.split(":")[1].strip()
            break
    return run_time
