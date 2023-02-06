# Parse the raw data
import os
import re
import json
import argparse
from utils import find_latest_dir, get_index_of_closing_bracket


def call_site_generator(requests, output_dir_str):
    callsite_counter = dict()
    for request in requests:
        # It is possible that a request does not have x-location header (CosmosDB service)
        if "x-location" not in request['httpRequest']['headers']:
            continue
            # print(request['httpRequest']['headers']['x-location'])
        x_location = str(request['httpRequest']['headers']['x-location'])
        if "\\tests\\" in x_location or \
                "\\Tests\\" in x_location or \
                "\\test\\" in x_location:
            continue
        callsite_counter[x_location] = callsite_counter.get(x_location, 0) + 1
    with open(os.path.join(output_dir_str, "CALLSITE.csv"), "w") as f:
        for key in sorted(callsite_counter.keys()):
            f.write("{}\t{}\n".format(key, callsite_counter[key]))
    f.close()
    return callsite_counter


def sdk_api_generator(requests, output_dir_str):
    sdk_api_counter = dict()
    empty_x_location_cnt = 0
    for request in requests:
        # It is possible that a request does not have x-location header (CosmosDB service)
        if "x-location" not in request['httpRequest']['headers']:
            continue
        x_location = str(request['httpRequest']['headers']['x-location'])
        if "\\tests\\" in x_location or \
                "\\Tests\\" in x_location or \
                "\\test\\" in x_location:
            continue
        if x_location == "[\', , ,\']":
            # print("empty x_location: {}".format(output_dir_str))
            # print(request['httpRequest']['method'])
            empty_x_location_cnt += 1
            continue
        else:
            try:
                # print(x_location)
                sdk_api = x_location.split(':', -1)[3]
            except:
                # print("Req not related to eval:" + x_location)
                # print(request)
                continue
            sdk_api_counter[sdk_api] = sdk_api_counter.get(sdk_api, 0) + 1
    # print(sdk_api_counter)
    with open(os.path.join(output_dir_str, "SDKAPI.csv"), "w") as f:
        for key in sorted(sdk_api_counter.keys()):
            f.write("{}\t{}\n".format(key, sdk_api_counter[key]))
    f.close()
    # if empty_x_location_cnt != 0:
    #     print("Number of empty x-Location value: {}".format(empty_x_location_cnt))
    return sdk_api_counter


def rest_api_generator(requests, output_dir_str):
    callsite_rest_map = dict()
    rest_api_counter = dict()

    f = open(os.path.join(output_dir_str, "RESTAPI.csv"), "w")
    f.write("REST\tNUM\n")

    for request in requests:
        # print(request['httpRequest']['headers']['x-location'])
        try:
            http_request = request['httpRequest']
            http_response = request['httpResponse']
            status_code = str(http_response["statusCode"])
            host = str(http_request['headers']['Host'][0])
        except:
            continue
        try:
            reason_phrase = str(http_response["reasonPhrase"])
        except:
            reason_phrase = ""
        http_method = str(http_request['method'])
        http_path = str(http_request['path'])
        # http_path_level = http_path.count("/")

        status_code = "status_code = " + status_code
        reason_phrase = "reason_phrase = " + reason_phrase
        request_path = "Path = " + http_path

        inject_info = ""
        if "headers" in http_response:
            if "injected" in http_response["headers"]:
                inject_info = "injected"
        query_info = []
        if "queryStringParameters" in http_request:
            http_query_string = http_request['queryStringParameters']
            for i in http_query_string:
                tmp_string = str(i) + "=" + str(http_query_string[i])
                query_info.append(tmp_string)

        sep = " "
        REST_info = [host, http_method, request_path, status_code, reason_phrase, inject_info] + query_info
        rest_api = sep.join(x for x in REST_info if x)
        f.write("{}\t{}\n".format(rest_api, 1))

        rest_api_counter[rest_api] = rest_api_counter.get(rest_api, 0) + 1

        # It is possible that a request does not have x-location header (CosmosDB service)
        if "x-location" not in request['httpRequest']['headers']:
            continue
        x_location = str(request['httpRequest']['headers']['x-location'])
        if x_location in callsite_rest_map:
            callsite_rest_map[x_location].add(rest_api)
        else:
            callsite_rest_map[x_location] = {rest_api}
    f.close()

    # for ele in callsite_rest_map:
    #     if len(callsite_rest_map[ele]) > 1:
    #         print(callsite_rest_map[ele])

    return rest_api_counter


def overview_generator(call_site_dict, sdk_api_dict, rest_api_dict, output_dir_str):
    call_site_num = sum(call_site_dict.values())
    rest_api_num = sum(rest_api_dict.values())
    sdk_api_num = sum(sdk_api_dict.values())

    uniq_call_site_num = len(call_site_dict.keys())
    uniq_rest_api_num = len(rest_api_dict.keys())
    uniq_sdk_api_num = len(sdk_api_dict.keys())

    # if call_site_num != rest_api_num:
    #     print("Call site number != REST API request number: ".format(output_dir_str))
    #
    # if call_site_num != sdk_api_num:
    #     print("Call site number != SDK API request number: ".format(output_dir_str))

    # Running time is recorded in Rainmaker infra
    with open(os.path.join(output_dir_str, "overview.txt"), "r") as f:
        lines = f.readlines()
        running_time_line = lines[0]
    f.close()

    with open(os.path.join(output_dir_str, "overview.txt"), "w") as f:
        f.write("{}".format(running_time_line))
        f.write("Call site number: {}\n".format(call_site_num))
        f.write("Unique call site number: {}\n".format(uniq_call_site_num))
        f.write("REST API number: {}\n".format(rest_api_num))
        f.write("Unique REST API number: {}\n".format(uniq_rest_api_num))
        f.write("SDK API number: {}\n".format(sdk_api_num))
        f.write("Unique SDK API number: {}\n".format(uniq_sdk_api_num))
    f.close()


class RawDataGenerator:
    # Class variables
    req_failed_and_has_first_callsite_cnt = 0
    req_success_and_has_second_callsite_cnt = 0
    request_num = 0
    # Test runs that have more that one injection points.
    more_than_one_injection_file = []

    def __init__(self, _result_dir_str, _is_put):
        # Instance Variable
        # The result directory is different for different instances.
        self.result_dir_str = _result_dir_str
        self.stat_directory = os.fsencode(_result_dir_str)
        self.is_put = _is_put

    # Generate all raw data files.
    def generate(self):
        # Test name as dir name
        for test_dir in os.listdir(self.stat_directory):
            test_dir_name = os.fsdecode(test_dir)
            test_dir_str = os.path.join(self.result_dir_str, test_dir_name)
            if os.path.isdir(test_dir_str):
                # Test round name as dir name, e.g., 0
                for test_round_dir in os.listdir(test_dir_str):
                    test_round_dir_str = os.path.join(test_dir_str, test_round_dir)
                    # print(test_round_dir_str)
                    for stat_file in os.listdir(test_round_dir_str):
                        # stat_file_name = os.fsencode(stat_file)
                        # print(stat_file)
                        if stat_file == "request.json":
                            request_path = os.path.join(test_round_dir_str, stat_file)
                            if os.path.getsize(request_path) > 0:
                                req_file = open(request_path)
                                # Parse PUT json file which contains multiple json arrays
                                if self.is_put == True:
                                    json_string = req_file.readlines()[0]
                                    pattern = '^\[\]'
                                    result = re.match(pattern, json_string)
                                    if result:
                                        req_file.close()
                                        continue
                                    index_cb = get_index_of_closing_bracket(json_string, 0)
                                    json_string = json_string[:index_cb + 1]
                                    data = json.loads(json_string)
                                else:
                                    data = json.load(req_file)

                                # Beautify the json file
                                with open(os.path.join(test_round_dir_str, "b_request.json"), "w") as f:
                                    f.write(json.dumps(data, sort_keys=True, indent=4))
                                # print("test_round_dir_str = " + test_round_dir_str )
                                call_site_cnt = call_site_generator(data, test_round_dir_str)
                                sdk_api_cnt = sdk_api_generator(data, test_round_dir_str)
                                rest_api_cnt = rest_api_generator(data, test_round_dir_str)
                                overview_generator(call_site_cnt, sdk_api_cnt, rest_api_cnt, test_round_dir_str)

                                self.__parse_traffic(data, request_path)

                            else:
                                print("{} is empty!".format(request_path))

        print("Request failed and has first unique call site {} out of {}".format(
            self.req_failed_and_has_first_callsite_cnt, self.request_num))
        print("Request succeeded and has second unique call site {}".format(
            self.req_success_and_has_second_callsite_cnt))

        # This is used to check whether the synchronization for injection is implemented successfully or not
        # print("Number of test run that has more than one injection point: {}".format(
        #     len(self.more_than_one_injection_file)))
        # for json_path in more_than_one_injection_file:
        #     print(json_path)

    # Parse the HTTP traffic to get statistics.
    def __parse_traffic(self, traffic, req_path):
        # Keep callsites that at least appear once.
        check_first_callsite = set()
        # Keep callsites that have a request that fails first.
        failed_req_first_callsite = set()
        # Keep callsites that have the first request failed and second request succeeded.
        check_success_second_callsite = set()

        inject_times = 0
        for req in traffic:
            if 'headers' in req['httpResponse']:
                if 'injected' in req['httpResponse']['headers']:
                    inject_times += 1
            self.request_num += 1
            status_code = req['httpResponse']['statusCode']

            # It is possible that a request does not have x-location header.
            if 'x-location' not in req['httpRequest']['headers']:
                continue
            x_location = str(req['httpRequest']['headers']['x-location'])
            if status_code >= 300:
                if x_location in check_first_callsite:
                    continue
                else:
                    check_first_callsite.add(x_location)
                    failed_req_first_callsite.add(x_location)
                    self.req_failed_and_has_first_callsite_cnt += 1
            elif status_code < 300:
                if x_location in failed_req_first_callsite and \
                        x_location not in check_success_second_callsite:
                    self.req_success_and_has_second_callsite_cnt += 1
                    check_success_second_callsite.add(x_location)
                else:
                    check_first_callsite.add(x_location)
        if inject_times > 1:
            self.more_than_one_injection_file.append(req_path)


if __name__ == "__main__":
    def_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
    # print("test_raw_data_generator def_directory: " + def_directory)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=def_directory, help="The directory to run analysis")
    parser.add_argument("-u", "--put_flag", default=False, help="Parameterized unit test flag")
    args = parser.parse_args()

    if args.dir != def_directory:
        tar_dir = os.path.join(os.getcwd(), "stat") + "/" + args.dir
    else:
        tar_dir = args.dir

    latest_stat_dir = tar_dir
    rdg = RawDataGenerator(latest_stat_dir, args.put_flag)
    rdg.generate()
