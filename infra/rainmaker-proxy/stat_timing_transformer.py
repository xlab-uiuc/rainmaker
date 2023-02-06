# load the csv table
# if run a single test for all the injection round (runnning time x request number - calculated time)
# sort all the running time of tests in an ascending order
# generate a graph: x: the number of the test in the sorted list  y: time how long it will take - calculated time
# graph could provide some rapid rising points; also some ranges to feasibly run; some ranges that is not feasibly to do


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime


def stat():
    directory_in_str = "C:\\Users\\yinfang\\rainmaker\\infra\\rainmaker-proxy\\stat\\Orleans"
    directory = os.fsencode(directory_in_str)

    dir_contains_larger_than_three = 0 
    dir_contains_three_files = 0
    dir_contains_two_files = 0
    dir_contains_single_file = 0
    dir_is_empty = 0
        
    callsite_arr = []
    uniq_callsite_arr = []
    rest_arr = []
    uniq_rest_arr = []
    runtime_arr = []

    suppose_failed_test_name_list = []

    df_result = pd.DataFrame()
    cnt = 0
    for file in os.listdir(directory):
        test_dir_name = os.fsdecode(file)
        dir_str = directory_in_str+"\\"+test_dir_name
        if os.path.isdir(dir_str): 
            # print("Test dir: {}".format(dir_str))

            # Some tests will not fire any requests, so the dir will be empty 
            if len(os.listdir(dir_str)) == 0:
                dir_is_empty += 1
                continue
            for case_dir in os.listdir(dir_str):
                # print("Test dir: {}".format(case_dir))
                case_dir_path = os.path.join(dir_str, case_dir)
                if os.path.isdir(case_dir_path):
                    # test round dir
                    initial_count = 0
                    # three files:
                    for path in os.listdir(case_dir_path):
                        file_path = os.path.join(case_dir_path, path)
                        if os.path.isfile(file_path):
                            initial_count += 1
                    # print(initial_count)
                    if initial_count == 0:
                        dir_is_empty += 1
                    elif initial_count == 1:
                        dir_contains_single_file += 1
                    elif initial_count == 2:
                        dir_contains_two_files += 1
                        suppose_failed_test_name_list.append(test_dir_name)
                    elif initial_count == 3:
                        dir_contains_three_files += 1
                        file = open(os.path.join(case_dir_path, 'overview.txt'))
                        content = file.readlines()

                        runtime_str = content[0].split(':')[1].lstrip().rstrip()
                        min_to_sec_time = 0
                        total_sec_time = 0
                        if runtime_str.__contains__('m'):
                            min_to_sec_time = int(runtime_str.split('m')[0]) * 60
                            sec_time = float(runtime_str.split('m')[1].split('s')[0].lstrip())
                            total_sec_time = min_to_sec_time + sec_time
                        else:
                            sec_time = float(runtime_str.split('s')[0].lstrip())

                        callsite_str = int(content[1].split(':')[1].lstrip().rstrip())
                        uniq_callsite_str = int(content[2].split(':')[1].lstrip().rstrip())
                        rest_str = int(content[3].split(':')[1].lstrip().rstrip())
                        uniq_rest_str = int(content[4].split(':')[1].lstrip().rstrip())

                        runtime_arr.append(min_to_sec_time+sec_time)
                        callsite_arr.append(callsite_str)
                        uniq_callsite_arr.append(uniq_callsite_str)
                        rest_arr.append(rest_str)
                        uniq_rest_arr.append(uniq_rest_str)
                        dataFrame = pd.read_csv(case_dir_path+"\\RESTAPI.csv", sep='\t', header=None, names=["REST_API", "#API"])
                        if cnt == 0:
                            df_result = dataFrame
                        else:
                            df_result = pd.concat([df_result, dataFrame])
                        cnt += 1
                    elif initial_count > 3:
                        dir_contains_larger_than_three += 1
                    continue
                else:
                    print("Not a test round stat dir")
        else:
            print("Not a test stat dir")
            exit(0)
    

    
    # print("The number of APIs covered is: {}".format(non_empty_api))
    
    # print("dir_is_empty: {}".format(dir_is_empty))
    # print("dir_contains_single_file: {}".format(dir_contains_single_file))
    # print("dir_contains_two_files: {}".format(dir_contains_two_files))
    # print("dir_contains_three_files: {}".format(dir_contains_three_files))
    # print("dir_contains_larger_than_three: {}".format(dir_contains_larger_than_three))
    results = pd.read_csv("stat\\dotnet-test-api-stats.txt", sep='\t', header=None)
    failed_results = pd.read_csv("stat\\failed-test-name-emulator.csv", sep='\t', header=None)
    failed_results_l = failed_results[0].tolist()
    results_l = results[1].tolist()
    for ele in failed_results_l:
        if ele in results_l:
            results_l.remove(ele)

    test_to_run = sum(results_l)
    test_finished_cnt = dir_contains_three_files + dir_contains_two_files + dir_is_empty

    # print("* # Total Tests to run -- {}".format(test_to_run))
    # print("* # Tests Finished -- {} / {}".format(test_finished_cnt, test_finished_cnt/test_to_run))

    print("* - # Test PASSED -- {}".format(dir_contains_three_files))
    print("* - # Test FAILED -- {}".format(dir_contains_two_files))
    print("* - # Test SKIPPED -- {}".format(dir_is_empty))

    df_result = df_result.groupby('REST_API')['#API'].sum()
    non_empty_api = np.count_nonzero(df_result, axis=0)

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    
    # print(df_result)
    print("* # REST APIs Covered -- {}".format(non_empty_api))
    print("---")

    total_time = sum(runtime_arr)
    avg_time = total_time / len(runtime_arr)
    print("Total test running time -- {} seconds (HH:MM:SS - {})".format(total_time, str(datetime.timedelta(seconds=total_time))))
    print("* - Avg Test Running Time --- {}".format(avg_time))
    p50 = pd.DataFrame(runtime_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(runtime_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(runtime_arr).quantile(0.90)[0]
    print("* P50 Test running time -- {}".format(p50))
    print("* P75 Test running time -- {}".format(p75))
    print("* P90 Test running time -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(callsite_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(callsite_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(callsite_arr).quantile(0.90)[0]
    print("* P50 # Callsites by a test -- {}".format(p50))
    print("* P75 # Callsites by a test -- {}".format(p75))
    print("* P90 # Callsites by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(uniq_callsite_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(uniq_callsite_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(uniq_callsite_arr).quantile(0.90)[0]
    print("* P50 # Unique callsites by a test -- {}".format(p50))
    print("* P75 # Unique callsites by a test -- {}".format(p75))
    print("* P90 # Unique callsites by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(rest_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(rest_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(rest_arr).quantile(0.90)[0]
    print("* P50 # REST APIs called by a test -- {}".format(p50))
    print("* P75 # REST APIs called by a test -- {}".format(p75))
    print("* P90 # REST APIs called by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(uniq_rest_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(uniq_rest_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(uniq_rest_arr).quantile(0.90)[0]
    print("* P50 # Unique REST APIs called by a test -- {}".format(p50))
    print("* P75 # Unique REST APIs called by a test -- {}".format(p75))
    print("* P90 # Unique REST APIs called by a test -- {}".format(p90))


    for e in suppose_failed_test_name_list:
        print(e)


def vanilla_stat():
    directory_in_str = "C:\\Users\\yinfang\\rainmaker\\infra\\rainmaker-proxy\\stat\\Orleans-Vanilla"
    directory = os.fsencode(directory_in_str)

    dir_contains_larger_than_three = 0 
    dir_contains_three_files = 0
    dir_contains_two_files = 0
    dir_contains_single_file = 0
    dir_is_empty = 0
        
    callsite_arr = []
    uniq_callsite_arr = []
    rest_arr = []
    uniq_rest_arr = []

    runtime_arr = []

    suppose_failed_test_name_list = []

    df_result = pd.DataFrame()
    cnt = 0
    for file in os.listdir(directory):
        test_dir_name = os.fsdecode(file)
        dir_str = directory_in_str+"\\"+test_dir_name
        if os.path.isdir(dir_str): 
            # print("Test dir: {}".format(filename))
            initial_count = 0
            for path in os.listdir(dir_str):
                if os.path.isfile(os.path.join(dir_str, path)):
                    initial_count += 1
            # print(initial_count)
            if initial_count == 0:
                dir_is_empty += 1
            elif initial_count == 1:
                dir_contains_single_file += 1
            elif initial_count == 2:
                dir_contains_two_files += 1
                suppose_failed_test_name_list.append(test_dir_name)
            elif initial_count == 3:
                dir_contains_three_files += 1
                file = open(os.path.join(dir_str, 'overview.txt'))
                content = file.readlines()
                callsite_str = int(content[1].split(':')[1].lstrip().rstrip())
                uniq_callsite_str = int(content[2].split(':')[1].lstrip().rstrip())
                rest_str = int(content[3].split(':')[1].lstrip().rstrip())
                uniq_rest_str = int(content[4].split(':')[1].lstrip().rstrip())

                runtime_str = content[0].split(':')[1].lstrip().rstrip()
                min_to_sec_time = 0
                total_sec_time = 0
                if runtime_str.__contains__('m'):
                    min_to_sec_time = int(runtime_str.split('m')[0]) * 60
                    sec_time = float(runtime_str.split('m')[1].split('s')[0].lstrip())
                    total_sec_time = min_to_sec_time + sec_time
                else:
                    sec_time = float(runtime_str.split('s')[0].lstrip())

                runtime_arr.append(total_sec_time)
                callsite_arr.append(callsite_str)
                uniq_callsite_arr.append(uniq_callsite_str)
                rest_arr.append(rest_str)
                uniq_rest_arr.append(uniq_rest_str)
                dataFrame = pd.read_csv(dir_str+"/RESTAPI.csv", sep='\t', header=None, names=["REST_API", "#API"])
                if cnt == 0:
                    df_result = dataFrame
                else:
                    df_result = pd.concat([df_result, dataFrame])
                cnt += 1
            elif initial_count > 3:
                dir_contains_larger_than_three += 1
            continue
        else:
            print("Not a test stat dir")
            exit(0)
    
    df_result = df_result.groupby('REST_API')['#API'].sum()
    non_empty_api = np.count_nonzero(df_result, axis=0)

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    test_to_run = 269 # for Orleans Azure test
    test_finished_cnt = 269
    print("* # Total Tests to run -- {}".format(test_to_run))
    print("* # Tests Finished -- {} / {}".format(test_finished_cnt, test_finished_cnt/test_to_run))
    # print(df_result)
    print("* # REST APIs Covered -- {}".format(non_empty_api))
    # print("The number of APIs covered is: {}".format(non_empty_api))

    print("* - # Test PASSED -- {}".format(dir_contains_three_files))
    print("* - # Test FAILED -- {}".format(dir_contains_two_files))
    print("* - # Test SKIPPED -- {}".format(test_to_run - dir_contains_three_files - dir_contains_two_files))
    print("---")

    total_time = sum(runtime_arr)
    avg_time = total_time / len(runtime_arr)
    print("Total test running time -- {} seconds (HH:MM:SS - {})".format(total_time, str(datetime.timedelta(seconds=total_time))))
    print("* - Avg Test Running Time --- {}".format(avg_time))
    p50 = pd.DataFrame(runtime_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(runtime_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(runtime_arr).quantile(0.90)[0]
    print("* P50 Test running time -- {}".format(p50))
    print("* P75 Test running time -- {}".format(p75))
    print("* P90 Test running time -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(callsite_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(callsite_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(callsite_arr).quantile(0.90)[0]
    print("* P50 # Callsites by a test -- {}".format(p50))
    print("* P75 # Callsites by a test -- {}".format(p75))
    print("* P90 # Callsites by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(uniq_callsite_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(uniq_callsite_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(uniq_callsite_arr).quantile(0.90)[0]
    print("* P50 # Unique callsites by a test -- {}".format(p50))
    print("* P75 # Unique callsites by a test -- {}".format(p75))
    print("* P90 # Unique callsites by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(rest_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(rest_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(rest_arr).quantile(0.90)[0]
    print("* P50 # REST APIs called by a test -- {}".format(p50))
    print("* P75 # REST APIs called by a test -- {}".format(p75))
    print("* P90 # REST APIs called by a test -- {}".format(p90))
    print("---")

    p50 = pd.DataFrame(uniq_rest_arr).quantile(0.5)[0]
    p75 = pd.DataFrame(uniq_rest_arr).quantile(0.75)[0]
    p90 = pd.DataFrame(uniq_rest_arr).quantile(0.90)[0]
    print("* P50 # Unique REST APIs called by a test -- {}".format(p50))
    print("* P75 # Unique REST APIs called by a test -- {}".format(p75))
    print("* P90 # Unique REST APIs called by a test -- {}".format(p90))
    print("---")


    # for e in suppose_failed_test_name_list:
    #     print(e)


if __name__ == "__main__":
    # vanilla_stat()
    graph_stat()
    