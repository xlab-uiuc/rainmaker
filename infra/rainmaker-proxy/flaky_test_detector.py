import numpy as np
import pandas as pd
import os
import datetime
import shutil
import xml.etree.ElementTree as ET

def collect_flaky_test_logs(proj_name):
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    azure_test_outcome = pd.read_csv("..\\..\\results\\orleans\\azure-test-outcomes.csv", sep="\t")
    
    outcome_num = len(azure_test_outcome.columns) - 1

    if outcome_num <= 1:
        print("There should at least be 2 test rounds to find flaky tests!")
        exit(0)
    
    # col_names = []
    # for i in range(1, len(azure_test_outcome.columns)):
    #     col_name = "OUTCOME_" + str(i)
    #     col_names.append(col_name)

    # convert dataframe into a list of list
    azure_test_outcome_list = azure_test_outcome.values.tolist()
    flaky_tests_list = []
    flaky_order_dict = dict()

    for test_outcome_list in azure_test_outcome_list:
        # Remove the test name which is the first element in the list
        unit_test_name = test_outcome_list.pop(0)
        if len(set(test_outcome_list)) > 1:
            flaky_tests_list.append(unit_test_name)
            for ele in set(test_outcome_list):
                order = test_outcome_list.index(ele)
                if unit_test_name not in flaky_order_dict:
                    flaky_order_dict[unit_test_name] = []
                    flaky_order_dict[unit_test_name].append(order)
                else:
                    flaky_order_dict[unit_test_name].append(order)

    proj_result_dir = "outcome"
    ts_list = []
    dir_list = []
    dir_ts_dict = {}
    ts_str_dict = {}
    # Construct the ts=>str dict and ts=>dir name dict
    for f in os.listdir(proj_result_dir):
        test_run_dir_name = os.fsdecode(f)
        ts_str = test_run_dir_name.split("_")[1]
        ts = datetime.datetime.strptime(ts_str, "%Y.%m.%d.%H.%M.%S")

        ts_list.append(ts)
        dir_list.append(test_run_dir_name)
        # ts => dir
        dir_ts_dict[ts] = test_run_dir_name
        # ts => ts string
        ts_str_dict[ts] = ts_str

    # Find the the corresponding timestamp based on the order of the outcome
    zipped_ts_dir_lists = zip(ts_list, dir_list)
    sorted_zipped_ts_dir_lists = sorted(zipped_ts_dir_lists)
    sorted_ts_dir = [dir_str for _, dir_str in sorted_zipped_ts_dir_lists]
    sorted_ts_list = sorted(ts_list)
    
    flaky_test_dir = "..\\..\\flaky_tests\\"+proj_name
    if not os.path.isdir(flaky_test_dir):
        os.makedirs(flaky_test_dir)

    for flaky_test in flaky_tests_list:
        # print(flaky_order_dict[flaky_test])
        for flaky_order in flaky_order_dict[flaky_test]:

            # order = 0 is the ealiest outcome
            flaky_log_path = proj_result_dir+"\\"+sorted_ts_dir[flaky_order]

            unit_test_ts = sorted_ts_list[flaky_order]

            flaky_outcome_log_path = flaky_log_path + "\\" + flaky_test
            # print(flaky_outcome_log_path)

            check_folder = os.path.isdir(flaky_test_dir+"\\"+flaky_test)
            if not check_folder:
                os.makedirs(flaky_test_dir+"\\"+flaky_test)
            for f in os.listdir(flaky_outcome_log_path):
                flaky_path = os.path.join(flaky_outcome_log_path, f)
                tree = ET.parse(flaky_path)
                root = tree.getroot()
                        
                for child in root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results'):
                    if child.attrib.get('outcome') == "Passed":
                        shutil.copyfile(flaky_path, flaky_test_dir+"\\"+flaky_test+"\\"+"PASS.log_"+ts_str_dict[unit_test_ts])
                    elif child.attrib.get('outcome') == "Failed":
                        shutil.copyfile(flaky_path, flaky_test_dir+"\\"+flaky_test+"\\"+"FAIL.log_"+ts_str_dict[unit_test_ts])
                    elif child.attrib.get('outcome') == "NotExecuted":
                        shutil.copyfile(flaky_path, flaky_test_dir+"\\"+flaky_test+"\\"+"SKIP.log_"+ts_str_dict[unit_test_ts])

if __name__ == "__main__":
    collect_flaky_test_logs("orleans")