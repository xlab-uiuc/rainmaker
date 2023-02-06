import pandas as pd
import datetime
import os
import json
import argparse
import pathlib
import re
from utils import find_latest_dir, transform_timing_into_seconds, create_test_run_result_dir, \
    get_index_of_closing_bracket


class StatGenerator:
    # API/callsite => test name   
    RESTAPI_dict = dict()
    SDKAPI_dict = dict()
    CALLSITE_dict = dict()
    test_running_dict = dict()
    test_running_time_dict = dict()

    uniq_test_RESTAPI_dict = dict()
    test_RESTAPI_dict = dict()

    uniq_test_SDKAPI_dict = dict()
    test_SDKAPI_dict = dict()

    uniq_test_CALLSITE_dict = dict()
    test_CALLSITE_dict = dict()

    def __init__(self, _path_dir, _proj, _put_flag):
        self.path_dir = _path_dir
        self.proj = _proj
        self.is_put = _put_flag

    def generate(self, result_dir_str):
        directory = os.fsencode(result_dir_str)
        # Test name as dir name
        for test_dir in os.listdir(directory):
            test_dir_name = os.fsdecode(test_dir)
            test_dir_str = result_dir_str + "/" + test_dir_name
            # print(test_dir_str)
            if os.path.isdir(test_dir_str):
                sub_dir_order = 0
                # Test round name as dir name, e.g., 0
                for test_round_dir in os.listdir(test_dir_str):
                    test_round_dir_str = test_dir_str + "/" + test_round_dir
                    # print(test_round_dir_str)
                    sub_dir_order += 1
                    for stat_file in os.listdir(test_round_dir_str):
                        # print(stat_file)
                        if stat_file == "RESTAPI.csv":
                            RESTAPI_path = test_round_dir_str + "/" + stat_file
                            if os.path.getsize(RESTAPI_path) > 0:
                                df_restapi = pd.read_csv(RESTAPI_path, header=None, sep='\t', names=['RESTAPI', "NUM"])
                                restapi_list = df_restapi['RESTAPI'].tolist()

                                for restapi in restapi_list:
                                    if restapi in self.RESTAPI_dict.keys():
                                        if test_dir_name not in self.RESTAPI_dict[restapi]:
                                            self.RESTAPI_dict[restapi].append(test_dir_name)
                                    else:
                                        self.RESTAPI_dict[restapi] = list()
                                        self.RESTAPI_dict[restapi].append(test_dir_name)
                        if stat_file == "SDKAPI.csv":
                            SDKAPI_path = test_round_dir_str + "/" + stat_file
                            if os.path.getsize(SDKAPI_path) > 0:
                                df_sdkapi = pd.read_csv(SDKAPI_path, header=None, sep='\t', names=['SDKAPI', "NUM"])
                                sdkapi_list = df_sdkapi['SDKAPI'].tolist()

                                uniq_sdk_num = len(sdkapi_list)
                                sdk_num = sum(df_sdkapi['NUM'].tolist())
                                self.uniq_test_SDKAPI_dict[test_dir_name] = uniq_sdk_num
                                self.test_SDKAPI_dict[test_dir_name] = sdk_num

                                for sdkapi in sdkapi_list:
                                    if sdkapi in self.SDKAPI_dict.keys():
                                        if test_dir_name not in self.SDKAPI_dict[sdkapi]:
                                            self.SDKAPI_dict[sdkapi].append(test_dir_name)
                                    else:
                                        self.SDKAPI_dict[sdkapi] = list()
                                        self.SDKAPI_dict[sdkapi].append(test_dir_name)
                            else:
                                uniq_sdk_num = 0
                                sdk_num = 0
                                self.uniq_test_SDKAPI_dict[test_dir_name] = uniq_sdk_num
                                self.test_SDKAPI_dict[test_dir_name] = sdk_num
                        if stat_file == "CALLSITE.csv":
                            CALLSITE_path = test_round_dir_str + "/" + stat_file
                            if os.path.getsize(CALLSITE_path) > 0:
                                df_callsite = pd.read_csv(CALLSITE_path, header=None, sep='\t',
                                                          names=['CALLSITE', "NUM"])
                                callsite_list = df_callsite['CALLSITE'].tolist()

                                uniq_callsite_num = len(callsite_list)
                                callsite_num = sum(df_callsite['NUM'].tolist())
                                self.uniq_test_CALLSITE_dict[test_dir_name] = uniq_callsite_num
                                self.test_CALLSITE_dict[test_dir_name] = callsite_num

                                for callsite in callsite_list:
                                    if callsite in self.CALLSITE_dict.keys():
                                        if test_dir_name not in self.CALLSITE_dict[callsite]:
                                            self.CALLSITE_dict[callsite].append(test_dir_name)
                                    else:
                                        self.CALLSITE_dict[callsite] = list()
                                        self.CALLSITE_dict[callsite].append(test_dir_name)
                            else:
                                uniq_callsite_num = 0
                                callsite_num = 0
                                self.uniq_test_CALLSITE_dict[test_dir_name] = uniq_callsite_num
                                self.test_CALLSITE_dict[test_dir_name] = callsite_num
                        if stat_file == "overview.txt":
                            req_file = open(test_round_dir_str + "/request.json")
                            if self.is_put == True:
                                json_string = req_file.readlines()[0]
                                pattern = '^\[\]'
                                result = re.match(pattern, json_string)
                                # if result:
                                #     print
                                #     req_file.close()
                                #     data = json.load(req_file)
                                #     break
                                index_cb = get_index_of_closing_bracket(json_string, 0)
                                json_string = json_string[:index_cb + 1]
                                data = json.loads(json_string)
                            else:
                                data = json.load(req_file)
                            # data = json.load(req_file)
                            req_file.close()
                            test_injection_flag = False
                            for req in data:
                                if 'headers' in req['httpResponse']:
                                    if "injected" not in req['httpResponse']['headers']:
                                        continue
                                # It is possible that a request does not have x-location header (CosmosDB service)
                                if "x-location" not in req['httpRequest']['headers']:
                                    continue
                                x_location = str(req['httpRequest']['headers']['x-location'])
                                if "#" in x_location:
                                    # print(x_location)
                                    x_location = x_location.split("#")[0]
                                if "\\tests\\" in x_location \
                                        or "\\Tests\\" in x_location \
                                        or "\\test\\" in x_location:
                                    # print(test_round_dir_str + x_location)
                                    test_injection_flag = True
                                    break
                                else:
                                    test_injection_flag = False
                                    # print(x_location)
                                    break
                            request_path = test_round_dir_str + "/" + stat_file
                            with open(request_path) as f:
                                lines = f.readlines()
                                for line in lines:
                                    if line.startswith("Running"):
                                        if test_injection_flag:
                                            running_time_txt = "0"
                                            running_time = 0
                                        else:
                                            running_time_txt = line.split(":")[1].strip()
                                            running_time = float(transform_timing_into_seconds(running_time_txt))
                                        # print(test_dir_name)
                                        # print(sub_dir_order)
                                        self.test_running_dict[test_dir_name + str(sub_dir_order)] = running_time
                                        self.test_running_time_dict[test_dir_name] = running_time_txt
                                    elif line.startswith("REST API number"):
                                        rest_num = int(line.split(":")[1].strip())
                                        self.test_RESTAPI_dict[test_dir_name] = rest_num
                                    elif line.startswith("Unique REST"):
                                        uniq_rest_num = int(line.split(":")[1].strip())
                                        self.uniq_test_RESTAPI_dict[test_dir_name] = uniq_rest_num
                                    else:
                                        continue

        print(self.test_running_dict)
        total_time = datetime.timedelta(seconds=sum(self.test_running_dict.values()))
        print("Total running timg: ")
        print(total_time)
        print("Total running timg (in hours): ")
        print("{:0.4f}".format(total_time.seconds / 3600))

        self.__write_to_f()

    def mv_files(self):
        latest_test_res_dir = "../../results/" + self.proj
        if not os.path.isdir(latest_test_res_dir):
            os.mkdir(latest_test_res_dir)
        self.__mv_REST_API_files()
        self.__mv_SDK_API_files()
        self.__mv_CALLSITE_files()
        self.__mv_test_time_file()

    def __write_to_f(self):
        with open('test_time.csv', 'w') as f:
            f.write("TEST_NAME\tTEST_TIME\n")
            for test_name in self.test_running_time_dict:
                f.write("%s\t%s\n" % (test_name, self.test_running_time_dict[test_name]))
        f.close()

        with open('REST_API.csv', 'w') as f:
            f.write("REST_API\tTESTS_CALLING_THE_REST_API\n")
            for restapi in sorted(self.RESTAPI_dict):
                f.write("%s\t%s\n" % (restapi, self.RESTAPI_dict[restapi]))
        f.close()

        with open('test_REST_API.csv', 'w') as f:
            f.write("TEST_NAME\t#REST_CALL\n")
            for test_name in sorted(self.test_RESTAPI_dict):
                f.write("%s\t%s\n" % (test_name, self.test_RESTAPI_dict[test_name]))
        f.close()

        with open('test_uniq_REST_API.csv', 'w') as f:
            f.write("TEST_NAME\t#UNIQUE_RESTAPI\n")
            for test_name in sorted(self.uniq_test_RESTAPI_dict):
                f.write("%s\t%s\n" % (test_name, self.uniq_test_RESTAPI_dict[test_name]))
        f.close()

        with open('SDK_API.csv', 'w') as f:
            f.write("SDK_API\tTESTS_CALLING_THE_SDK_API\n")
            for sdkapi in self.SDKAPI_dict:
                f.write("%s\t%s\n" % (sdkapi, self.SDKAPI_dict[sdkapi]))
        f.close()

        with open('test_SDK_API.csv', 'w') as f:
            f.write("TEST_NAME\t#SDKAPI\n")
            for test_name in sorted(self.test_SDKAPI_dict):
                f.write("%s\t%s\n" % (test_name, self.test_SDKAPI_dict[test_name]))
        f.close()

        with open('test_uniq_SDK_API.csv', 'w') as f:
            f.write("TEST_NAME\t#UNIQUE_SDKAPI\n")
            for test_name in sorted(self.uniq_test_SDKAPI_dict):
                f.write("%s\t%s\n" % (test_name, self.uniq_test_SDKAPI_dict[test_name]))
        f.close()

        with open('CALLSITE.csv', 'w') as f:
            f.write("CALLSITE\tTESTS_CALLING_THE_CALLSITE\n")
            for callsite in self.CALLSITE_dict:
                f.write("%s\t%s\n" % (callsite, self.CALLSITE_dict[callsite]))
        f.close()

        with open('test_CALLSITE.csv', 'w') as f:
            f.write("TEST_NAME\t#CALLSITE\n")
            for test_name in sorted(self.test_CALLSITE_dict):
                f.write("%s\t%s\n" % (test_name, self.test_CALLSITE_dict[test_name]))
        f.close()

        with open('test_uniq_CALLSITE.csv', 'w') as f:
            f.write("TEST_NAME\t#UNIQUE_CALLSITE\n")
            for test_name in sorted(self.uniq_test_CALLSITE_dict):
                f.write("%s\t%s\n" % (test_name, self.uniq_test_CALLSITE_dict[test_name]))
        f.close()

    def __mv_REST_API_files(self):
        # REST API:
        df_REST = pd.read_csv("REST_API.csv", sep='\t')
        # Put the file under full collection folder
        df_REST.to_csv("../../results/" + self.proj + "/REST_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_REST.to_csv(self.path_dir + "/REST_API.csv", sep='\t', index=False)

        df_REST = pd.read_csv("test_REST_API.csv", sep='\t')
        # Put the file under full collection folder
        df_REST.to_csv("../../results/" + self.proj + "/test_REST_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_REST.to_csv(self.path_dir + "/test_REST_API.csv", sep='\t', index=False)

        df_REST = pd.read_csv("test_uniq_REST_API.csv", sep='\t')
        # Put the file under full collection folder
        df_REST.to_csv("../../results/" + self.proj + "/test_uniq_REST_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_REST.to_csv(self.path_dir + "/test_uniq_REST_API.csv", sep='\t', index=False)

    def __mv_SDK_API_files(self):
        # SDK API:
        df_SDK = pd.read_csv("SDK_API.csv", sep='\t')
        # Put the file under full collection folder
        df_SDK.to_csv("../../results/" + self.proj + "/SDK_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_SDK.to_csv(self.path_dir + "/SDK_API.csv", sep='\t', index=False)

        df_SDK = pd.read_csv("test_SDK_API.csv", sep='\t')
        # Put the file under full collection folder
        df_SDK.to_csv("../../results/" + self.proj + "/test_SDK_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_SDK.to_csv(self.path_dir + "/test_SDK_API.csv", sep='\t', index=False)

        df_SDK = pd.read_csv("test_uniq_SDK_API.csv", sep='\t')
        # Put the file under full collection folder
        df_SDK.to_csv("../../results/" + self.proj + "/test_uniq_SDK_API.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_SDK.to_csv(self.path_dir + "/test_uniq_SDK_API.csv", sep='\t', index=False)

    def __mv_CALLSITE_files(self):
        # CALLSITE:
        df_CALLSITE = pd.read_csv("CALLSITE.csv", sep='\t')
        # Put the file under full collection folder
        df_CALLSITE.to_csv("../../results/" + self.proj + "/CALLSITE.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_CALLSITE.to_csv(self.path_dir + "/CALLSITE.csv", sep='\t', index=False)

        df_CALLSITE = pd.read_csv("test_CALLSITE.csv", sep='\t')
        # Put the file under full collection folder
        df_CALLSITE.to_csv("../../results/" + self.proj + "/test_CALLSITE.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_CALLSITE.to_csv(self.path_dir + "/test_CALLSITE.csv", sep='\t', index=False)

        df_CALLSITE = pd.read_csv("test_uniq_CALLSITE.csv", sep='\t')
        # Put the file under full collection folder
        df_CALLSITE.to_csv("../../results/" + self.proj + "/test_uniq_CALLSITE.csv", sep='\t', index=False)
        # Put the file under latest round folder
        df_CALLSITE.to_csv(self.path_dir + "/test_uniq_CALLSITE.csv", sep='\t', index=False)

    def __mv_test_API_file(self):
        df = pd.read_csv("test_API_stats.csv")
        # Put the file under result collection folder
        df.to_csv("../../results/" + self.proj + "/test_API_stats.csv", index=False)
        # Put the file under latest round folder
        df.to_csv(self.path_dir + "/test_API_stats.csv", index=False)

    def __mv_test_time_file(self):
        df = pd.read_csv("test_time.csv", sep="\t")
        # Put the file under project result folder.
        df.to_csv("../../results/" + self.proj + "/test_time.csv", index=False)
        # Put the file under latest round folder too.
        df.to_csv(self.path_dir + "/test_time.csv", index=False)


# Obsolete
def merge_test_stat_results():
    vanilla_results = pd.read_csv("../../results/orleans/legacy-data/vanilla-sep-test-running-time-stats.txt",
                                  sep='\t',
                                  header=None, names=["TEST_NAME", "VANILLA_RUN_TIME"])
    runtime_results = pd.read_csv("test-running-time-stats.txt", sep='\t', header=None,
                                  names=["TEST_NAME", "INSTRUMENTED_RUN_TIME"])

    uniq_api = pd.read_csv("test_uniq_REST_API.csv", sep='\t')

    api = pd.read_csv("test_REST_API.csv", sep='\t')

    uniq_callsite = pd.read_csv("test_uniq_CALLSITE.csv", sep='\t')

    callsite = pd.read_csv("test_CALLSITE.csv", sep='\t')

    uniq_SDKAPI = pd.read_csv("test_uniq_SDK_API.csv", sep='\t')

    SDKAPI = pd.read_csv("test_SDK_API.csv", sep='\t')

    df_outer1 = pd.merge(runtime_results, vanilla_results, on='TEST_NAME', how='inner')
    df_outer2 = pd.merge(df_outer1, uniq_api, on='TEST_NAME', how='outer')
    df_outer3 = pd.merge(df_outer2, api, on='TEST_NAME', how='outer')
    df_outer4 = pd.merge(df_outer3, uniq_callsite, on='TEST_NAME', how='outer')
    df_outer5 = pd.merge(df_outer4, callsite, on='TEST_NAME', how='outer')
    df_outer6 = pd.merge(df_outer5, uniq_SDKAPI, on='TEST_NAME', how='outer')
    df_outer7 = pd.merge(df_outer6, SDKAPI, on='TEST_NAME', how='outer')

    df_outer7["INSTRUMENTED_RUN_TIME_IN_SECONDS"] = df_outer7["INSTRUMENTED_RUN_TIME"] \
        .transform(transform_timing_into_seconds)
    df_outer7.to_csv('test_API_stats.csv', index=False)


if __name__ == "__main__":
    def_proj = "orleans"
    def_directory = find_latest_dir("stat")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=def_directory, help="The directory to run analysis")
    parser.add_argument("-p", "--proj", default=def_proj, help="The project to persist the results for")
    parser.add_argument("-u", "--put_flag", default=False, help="Parameterized unit test flag")

    args = parser.parse_args()

    if args.dir != def_directory:
        tar_dir = "stat/" + args.dir
    else:
        tar_dir = args.dir

    latest_stat_dir = tar_dir
    dir_name = pathlib.PurePath(tar_dir).name
    path_dir = create_test_run_result_dir("../../results", dir_name)

    sg = StatGenerator(path_dir, args.proj, args.put_flag)
    sg.generate(latest_stat_dir)
    sg.mv_files()
