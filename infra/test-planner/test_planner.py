import ast
import datetime
import json
import sys
import os
import random
import json
import argparse
import pandas as pd
from unittest import result

sys.path.append('../rainmaker-proxy')
from utils import transform_timing_into_seconds, find_latest_dir, find_second_latest_dir, find_third_latest_dir

def_directory = "../../results/" + find_third_latest_dir("stat")
def_request = find_second_latest_dir("stat")
def_response = find_latest_dir("stat")

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", default=def_directory, help="The directory to run analysis")
parser.add_argument("-req", "--request", default=def_request, help="Request injection failures")
parser.add_argument("-res", "--response", default=def_response, help="Response injection failures")

args = parser.parse_args()
if args.dir != def_directory:
    tar_dir = "../../results/" + args.dir
else:
    tar_dir = args.dir


def read_passed_tests():
    passed_test_list = list()
    with open(tar_dir + '/PASSED_test.csv') as f:
        for line in f.readlines():
            passed_test_list.append(line.strip())
    f.close()
    # print(passed_test_list)
    rest_test_list = list()
    with open(tar_dir + '/all_test_observed_at_REST_layer.csv') as f:
        next(f)
        for line in f.readlines():
            rest_test_list.append(line.strip())
    f.close()
    callsite_set = set()
    with open(tar_dir + '/CALLSITE.csv') as f:
        next(f)
        variables = dict()
        for line in f.readlines():
            item = line.split('\t')
            callsite = ast.literal_eval(item[0]).pop()
            test_list = ast.literal_eval(item[1])
            for ele in test_list:
                callsite_set.add(ele)
    # print(len(callsite_set)) 
    # print(len(set(passed_test_list) & callsite_set))  
    # print("Length after intersection: "+str(len(list(set(passed_test_list) & set(rest_test_list) & callsite_set))))         
    return list(set(passed_test_list) & set(rest_test_list) & callsite_set)


def read_test_running_time():
    test_time_dict = dict()
    with open(tar_dir + '/test_time.csv') as f:
        next(f)
        for line in f.readlines():
            # print(line)
            item = line.split(',')
            test_name = item[0]
            time = float(transform_timing_into_seconds(item[1]))
            test_time_dict[test_name] = time
    return test_time_dict


def read_test_callsites():
    test_callsites = dict()
    callsite_set = set()
    test_set = set()
    with open(def_directory + '/CALLSITE.csv') as f:
        next(f)
        for line in f.readlines():
            item = line.split('\t')
            callsite = ast.literal_eval(item[0]).pop()
            callsite_set.add(callsite)
            test_list = ast.literal_eval(item[1])
            # Construct test => call sites mapping
            for test in test_list:
                test_set.add(test)
                if test not in test_callsites.keys():
                    test_callsites[test] = set()
                    test_callsites[test].add(callsite)
                else:
                    test_callsites[test].add(callsite)
    return test_callsites, callsite_set, test_set


# Objective 0: cover all tests in test suite - randomly pick one call site
def cover_all_tests(req_f, res_f):
    passed_tests = read_passed_tests()
    test_time_dict = read_test_running_time()

    for key in list(test_time_dict):
        if key not in passed_tests:
            test_time_dict.pop(key, None)

    total_time = datetime.timedelta(seconds=sum(test_time_dict.values()))
    total_hrs = total_time.seconds / 3600
    print("Objective 0 (covering all tests in test suite - randomly pick one call site for each test): {:0.4f}".format(
        total_hrs))
    print("Number of test plans: {}".format(len(test_time_dict)))
    test_callsites_map, _, _ = read_test_callsites()
    with open("obj0-output.csv", "w") as out:
        for key in test_callsites_map.keys():
            first_callsite_in_map = random.choice(tuple(test_callsites_map[key]))
            out.write(key + "\t" + first_callsite_in_map + "\n")
    out.close()
    # TODO: make it configurable
    # find_common_test_plan("obj0-output.csv", res_f, "obj0-timeout-injection")
    # find_common_test_plan("obj0-output.csv", req_f, "obj0-request-block")


# Objective 1: only cover unique SDK call sites
def cover_all_callsites(req_f, res_f):
    test_time = read_test_running_time()
    callsite_test_injection = dict()
    total_time_l = list()
    count_callsite = 0
    # Read uniq callsites from CALLSITE.csv
    with open(tar_dir + '/CALLSITE.csv') as f:
        with open("obj1-output.csv", "w") as out:
            next(f)
            for line in f.readlines():
                if "\\tests\\" in line:
                    continue
                count_callsite += 1
                item = line.split('\t')
                callsite = ast.literal_eval(item[0]).pop()
                test_list = ast.literal_eval(item[1])
                call_test_time_d = dict()
                for ele in test_list:
                    call_test_time_d[ele] = test_time[ele]
                    # print(ele)
                chosen_test = min(call_test_time_d, key=call_test_time_d.get)
                chosen_time = call_test_time_d[chosen_test]
                total_time_l.append(chosen_time)
                callsite_test_injection[callsite] = chosen_test
                out.write(chosen_test + "\t" + callsite + "\n")
                # print(chosen_test)
    f.close()
    out.close()
    total_time = datetime.timedelta(seconds=sum(total_time_l))
    total_hrs = total_time.seconds / 3600
    print("Objective 1 (covering unique SDK API call sites): {:0.4f}".format(total_hrs))
    print("Number of test plans: {}".format(count_callsite))

    # TODO: make it configurable
    # find_common_test_plan("obj1-output.csv", res_f, "obj1-timeout-injection")
    # find_common_test_plan("obj1-output.csv", req_f, "obj1-request-block")


# Objective 2: cover test and unique SDK call site in a pair-wise way - Linear programming
def cover_T_S_pairwise():
    passed_tests = read_passed_tests()
    test_time = read_test_running_time()
    # Construct the model - generate a JSON file
    model = dict()
    model["optimize"] = "time"
    model["opType"] = "min"
    test_set = set()
    callsite_set = set()
    # Variables generation: Read from CALLSITE.csv to get the mapping: unique call site => list of test names
    # with open('../../results/orleans/CALLSITE.csv') as f:
    with open(tar_dir + '/CALLSITE.csv') as f:
        next(f)
        variables = dict()
        for line in f.readlines():
            # if "\\tests\\" in line:
            #         continue
            item = line.split('\t')
            callsite = ast.literal_eval(item[0]).pop()
            test_list = ast.literal_eval(item[1])
            # Construct a variable for a call site <=> test name pair
            for test in test_list:
                if test not in passed_tests:
                    continue
                callsite_set.add(callsite)
                test_set.add(test)
                var_dict = dict()
                var_dict["time"] = test_time[test]
                var_dict[callsite] = 1
                var_dict[test] = 1
                var_name = test + "#" + callsite
                variables[var_name] = var_dict
    f.close()
    # Constraints generation
    constraints = dict()
    for uniq_callsite in callsite_set:
        constraints[uniq_callsite] = {"min": 1}
    for uniq_test in test_set:
        constraints[uniq_test] = {"min": 1}

    model["constraints"] = constraints
    model["variables"] = variables

    with open('obj2.json', 'w') as outfile:
        json.dump(model, outfile, indent=4)
        model_json = json.dumps(model, indent=4)
        # print(model_json)
    outfile.close()
    cmd = 'node -e "require(\\"%s\\").init()"' % ('./lp_planner')
    pipeline = os.popen(cmd)
    read_time = pipeline.read()
    print(read_time)
    read_time = float(read_time[:-2])
    total_hrs = read_time / 3600
    print("Objective 2 cover test and unique SDK call site in a pair-wise way: {:0.4f}".format(total_hrs))


def cover_T_S_pairwise_output(req_f, res_f):
    f = open("obj2-result.json")
    jdata = json.load(f)
    cnt = 0
    with open('obj2-output.csv', 'w') as out:
        for key, _ in jdata.items():
            if key in ["feasible", "result", "bounded"]:
                continue
            cnt += 1
            str_l = key.split("#", 1)
            out.write(str_l[0] + "\t" + str_l[1] + "\n")
    out.close()

    print("Number of test plans: {}".format(cnt))
    # TODO: make it configurable
    # find_common_test_plan("obj2-output.csv", res_f, "obj2-timeout-injection")
    # find_common_test_plan("obj2-output.csv", req_f, "obj2-request-block")


# Objective 3: cover every combination of (test, unique SDK call sites)
def cover_unique_T_S():
    passed_tests = read_passed_tests()
    test_time = read_test_running_time()
    total_time_l = list()
    counter = 0
    # with open('../../results/orleans/test_uniq_CALLSITE.csv') as f:
    with open(tar_dir + '/test_uniq_CALLSITE.csv') as f:
        next(f)
        for line in f.readlines():
            if "\\tests\\" in line:
                continue
            item = line.split('\t')
            test_name = item[0]
            if test_name not in passed_tests:
                continue
            num_api = int(item[1])
            total_time_l.append(num_api * test_time[test_name])
            counter += num_api
    f.close()
    total_time = datetime.timedelta(seconds=sum(total_time_l))
    total_hrs = total_time.seconds / 3600
    print("Objective 3 cover every combination of (test, unique SDK call sites): {:0.4f}".format(total_hrs))
    print("Number of test plans: {}".format(counter))


# Objective 4: cover every combination of (test, SDK call sites)
def cover_every_T_S():
    test_time = read_test_running_time()
    total_time_l = list()
    counter = 0
    # with open('../../results/orleans/test_CALLSITE.csv') as f:
    with open(tar_dir + '/test_CALLSITE.csv') as f:
        next(f)
        for line in f.readlines():
            if "\\tests\\" in line:
                continue
            item = line.split('\t')
            test_name = item[0]
            num_api = int(item[1])
            total_time_l.append(num_api * test_time[test_name])
            counter += num_api
    f.close()
    total_time = datetime.timedelta(seconds=sum(total_time_l))
    total_hrs = total_time.seconds / 3600
    print("Objective 4 cover every combination of (test, SDK call sites): {:0.4f}".format(total_hrs))
    print("Number of test plans: {}".format(counter))


def find_common_test_plan(test_plan_f, failure_f, obj_str):
    df = pd.read_csv(os.path.join("../../results", failure_f, "bug_inspection.csv"), sep='\t')
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #    print(df['SDK'])
    common_injection = list()
    with open(test_plan_f) as f:
        lines = f.readlines()
        for line in lines:
            ele = line.strip().split("\t")
            test_name = ele[0]
            # if(test_plan_f == "obj2-output.csv"):
            #     print(test_name)
            call_site = ele[1]
            # if(test_plan_f == "obj2-output.csv"):
            #     print(call_site)
            if ((df['name'] == test_name) & (df['SDK'] == call_site)).any():
                common_injection.append(line)
    f.close()
    # print("Common injection points:")
    # print(common_injection)
    with open(obj_str + '-common.csv', 'w') as outfile:
        for ele in common_injection:
            outfile.write(ele)
    outfile.close()


if __name__ == "__main__":
    cover_all_tests(args.request, args.response)
    cover_all_callsites(args.request, args.response)
    cover_T_S_pairwise()
    cover_T_S_pairwise_output(args.request, args.response)
    cover_unique_T_S()
    cover_every_T_S()

# For BotBuilder
# def_directory = "../../results/Botbuilder-dotnet_2022.05.06.06.00.32"
# def_request = "Botbuilder-dotnet-injection-round-500timeout_2022.05.06.06.33.24"
# def_response = "Botbuilder-dotnet-injection-round-503Req_2022.05.09.07.09.34"

# For Insights
# def_directory = "../../results/Insights_2022.06.12.18.16.23"
# def_request = "Insights-injection-round-request-block_2022.06.13.15.52.16"
# def_response = "Insights-injection-round-status-code_2022.06.12.20.10.32"

# For sleet
# def_directory = "../../results/sleet_2022.07.25.11.54.00"
# def_request = "sleet-injection-round_2022.07.25.12.45.53"
# def_response = "sleet-injection-round_2022.07.25.12.07.33"

# For ironpigeon
# def_directory = "../../results/IronPigeon_2022.09.13.22.07.03"
# def_request = "storage-injection-round_2022.07.30.23.52.39"
# def_response = "storage-injection-round_2022.07.30.14.59.00"

# For efcore
# def_directory = "../../results/efcore_2022.08.04.20.55.22"
# def_request = "efcore-injection-round_2022.08.25.12.55.51"
# def_response = "efcore-injection-round_2022.08.05.14.48.12"

# For storage aws
# def_directory = "../../results/storage-aws_2022.07.18.13.57.02"
# def_request = "storage-injection-round_2022.07.30.23.52.39"
# def_response = "storage-injection-round_2022.07.30.14.59.00"

# For Distributedlock
# def_directory = "../../results/DistributedLock_2022.05.13.05.29.54"
# def_request = "DistributedLock-injection-round_2022.05.14.21.16.36"
# def_response = "DistributedLock-injection-round_2022.05.13.14.59.00"

# For efcore
# def_directory = "../../results/efcore_2022.08.04.20.55.22"
# def_request = "efcore-injection-round_2022.08.25.12.55.51"
# def_response = "efcore-injection-round_2022.08.05.14.48.12"

# For ServiceStack
# def_directory = "../../results/servicestack_2022.07.19.20.50.26"
# def_request = "servicestack-injection-round_2022.07.25.15.25.04"
# def_response = "servicestack-injection-round-blind_2022.07.20.02.17.16"

# For Orleans
# def_directory = "../../results/Orleans_2022.02.25.00.09.00"
# def_request = "Orleans-injection-round-503Req_2022.04.03.02.14.36"
# def_response = "Orleans-injection-round-500timeout_2022.02.25.20.31.34"

# def_directory = "../../results/Akka.Persistence.Azure_2022.05.27.14.27.20"
# def_request = "Akka.Persistence.Azure-injection-round-request-block_2022.06.03.17.54.39"
# def_response = "Akka.Persistence.Azure-injection-round-status-code_2022.06.03.14.46.12"
