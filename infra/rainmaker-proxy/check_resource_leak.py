from collections import Counter
from utils import return_latest_dir_name
import json
import glob
import os
import csv
import argparse

'''
Now we only focus on POST, DELETE, PUT
The design of now is to compare the RESTAPI.csv of vanilla to the one of the injected round
'''
descp = "This is resource leak file generator"

# def_proj = "Insights"
def_proj = "Orleans"
# def_round = "Insights-injection-round-status-code_2022.09.02.12.45.19"
def_round = "Orleans-injection-round-timeout_2022.08.25.14.45.40"
# return_latest_dir_name("stat")
# def_vanilla_round = "Insights_2022.08.24.09.54.57"
def_vanilla_round = "Orleans_2022.08.18.15.00.35"
# True for local resource check, and false for remote resource check
def_local = False

parser = argparse.ArgumentParser(
    description=descp, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--round", "-r", default=def_round,
                    help="The injection round (normally should be the latest one with timestamp)")
parser.add_argument("--vanilla", "-v", default=def_vanilla_round,
                    help="The vanilla round without any injection")
parser.add_argument("--project", "-p", default=def_proj,
                    help="The project name")
parser.add_argument("--local", "-l", default=def_local,
                    help="True for local resource test and False for remote resource test")
args = parser.parse_args()

stat_dir = os.path.join("stat", args.round)
vanilla_dir = os.path.join("stat", args.vanilla)


def get_vanilla_REST(test_result_file):

    test_inject_dir = os.path.split(os.path.split(test_result_file)[0])[0]
    test_inject_name = os.path.split(test_inject_dir)[1]

    test_vanilla_REST_dir = vanilla_dir + "\\" + \
        test_inject_name + "\\0\\RESTAPI.csv"

    return test_vanilla_REST_dir


def check_resource_leak(result_dir):
    # print("INTO CHECK RESOURCE LEAK")
    # result_map = {}
    test_result_files = glob.glob(
        os.path.join(result_dir, "**", "RESTAPI.csv"), recursive=True)
    output_dir_proj = os.path.join("../../results", args.round)
    if args.local:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_local.csv")
    else:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_remote.csv")
    # print(bug_f_path)
    f = open(bug_f_path, "w", encoding="utf-8")
    f.write("Name\tTurn\tLeak\n")
    for test_result_file in test_result_files:
        # print(test_result_file)
        vanilla_REST = get_vanilla_REST(test_result_file)

        test_info = test_result_file.split('\\')
        test_name = test_info[-3]
        test_turn = test_info[-2]
        # print(test_name)
        # print(test_turn)
        cmp_result = compare(test_result_file, vanilla_REST)

        if not cmp_result[0]:
            # print(cmp_result[1])
            diff = str(cmp_result[1])
            # print(diff)
            f.write("{}\t{}\t{}\n".format(test_name, test_turn,diff))

    f.close()


def compare(test_result_file, vanilla_REST):
    # print("INTO_COMPARE")

    test_dir = test_result_file
    vanilla_dir = vanilla_REST
    test_path = set()
    vanilla_path = set()
    test_resource = 0
    vanilla_resource = 0
    # Now We only focus on Azure Storage Service and Cosmos

    with open(test_dir, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        for row in rows:
            rest = row["REST"]
            split_list = rest.split(" ")
            if(len(split_list) >= 5):
                test_path.add(split_list[4])
    
    with open(vanilla_dir, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        for row in rows:
            rest = row["REST"]
            split_list = rest.split(" ")
            if(len(split_list) >= 5):
                vanilla_path.add(split_list[4])
    
    #Find common part of REST API.
    if(test_path.isdisjoint(vanilla_path)):
        return (True, 0)
    else:
        common_path = vanilla_path.intersection(test_path)
        # print(common_path)

    with open(test_dir, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        for row in rows:
            rest = row["REST"]
            #Get path and compare it with Common part
            split_list = rest.split(" ")
            if(len(split_list) >= 5):
                tmp_path = split_list[4]
                if(tmp_path not in common_path):
                    continue
            else:
                continue

            if args.local:
                print("we have ditched local resource leak design")
           
            else:
                if (("PUT" in rest or "DELETE" in rest or "POST" in rest)) and \
                    (":8081" in rest or ":10000" in rest or ":10001" in rest or ":10002" in rest) and \
                    ("reason_phrase = Created" in rest or
                     "reason_phrase = No Content" in rest or
                     "reason_phrase = Accepted" in rest) :
                    if ("PUT" in rest or "POST" in rest) and "reason_phrase = Created" in rest:
                        test_resource += 1
                    elif ("DELETE" in rest and ("reason_phrase = No Content" in rest or "reason_phrase = Accepted" in rest) ):
                        test_resource -= 1

    with open(vanilla_dir, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        for row in rows:
            rest = row["REST"]
            #Get path and compare it with Common part
            split_list = rest.split(" ")
            if(len(split_list) >= 5):
                tmp_path = split_list[4]
                if(tmp_path not in common_path):
                    continue
            else:
                continue

            if args.local:
                print("we have ditched local resource leak design")
            else:
                if (("PUT" in rest or "DELETE" in rest or "POST" in rest)) and \
                    (":8081" in rest or ":10000" in rest or ":10001" in rest or ":10002" in rest) and \
                    ("reason_phrase = Created" in rest or
                     "reason_phrase = No Content" in rest or
                     "reason_phrase = Accepted" in rest):
                    if ("PUT" in rest or "POST" in rest) and "reason_phrase = Created" in rest:
                        vanilla_resource += 1
                    elif ("DELETE" in rest and ("reason_phrase = No Content" in rest or "reason_phrase = Accepted" in rest) ):
                        vanilla_resource -= 1

    return ( (vanilla_resource == test_resource), (test_resource - vanilla_resource) )

if __name__ == "__main__":
    # print(stat_dir)
    check_resource_leak(stat_dir)

