from collections import Counter
from utils import return_latest_dir_name
import json
import os
import csv
import argparse
import pandas as pd
import filecmp
'''
Now we only focus on POST, DELETE, PUT
The design of now is to compare the RESTAPI.csv of vanilla to the one of the injected round
'''
descp = "This is resource leak file generator"

def_proj = "Insights"
# def_proj = "Orleans"
def_round = "Insights-injection-round-status-code_2022.09.02.12.45.19"
# def_round = "Orleans-injection-round-blind-all-true_2022.08.21.01.13.39"
# return_latest_dir_name("stat")
def_vanilla_1 = "Insights_2022.08.24.09.54.57"
def_vanilla_2 = "Insights_2022.09.14.02.14.35"
# def_vanilla_round = "Orleans_2022.08.18.15.00.35"

# True for local resource check, and false for remote resource check
def_local = False

parser = argparse.ArgumentParser(
    description=descp, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--round", "-r", default=def_round,
                    help="The injection round (normally should be the latest one with timestamp)")
parser.add_argument("--vanilla_1", "-v1", default=def_vanilla_1,
                    help="The first vanilla round without any injection")
parser.add_argument("--vanilla_2", "-v2", default=def_vanilla_2,
                    help="The second vanilla round without any injection")
parser.add_argument("--project", "-p", default=def_proj,
                    help="The project name")
parser.add_argument("--local", "-l", default=def_local,
                    help="True for local resource test and False for remote resource test")
args = parser.parse_args()

stat_dir = os.path.join("stat", args.round)

vanilla_1_dir = os.path.join("stat", args.vanilla_1)
vanilla_2_dir = os.path.join("stat", args.vanilla_2)

def compare(dir_1, dir_2):
    # print("INTO_COMPARE")

    file_1 = dir_1
    file_2 = dir_2
    # test_dict = {}
    # vanilla_dict = {}
    # test_resource = 0
    # vanilla_resource = 0
    # test_list = []
    # vanilla_list = []

    result = filecmp.cmp(file_1, file_2, shallow = False)
    # Now We only focus on Azure Storage Service and Cosmos
    # with open(file_1, newline='') as injection_result:
    #     rows = csv.DictReader(injection_result, delimiter='\t')
    #     for row in rows:
    #         rest = row["REST"]
    #         if args.local:
    #             print("We have ditched the local resource leak check design")
    #             # if ("PUT" in rest or "DELETE" in rest or "POST" in rest) and \
    #             #     ("comp = lease" not in rest) and \
    #             #     ("/$batch" not in rest) and \
    #             #     ("status_code = 2" in rest):
    #             #     #Cosmos Service, we does not specify the exact resource of Cosmos now due to too many kinds of Cosmos service.
    #             #     if (":8081" in rest):
    #             #         if ("PUT" in rest or "POST" in rest) and "reason_phrase = Created" in rest:
    #             #             test_dict["Cosmos"] = test_dict.get("Cosmos", 0) + 1
    #             #             test_resource += 1
    #             #         elif ("reason_phrase = No Content"):
    #             #             test_dict["Cosmos"] = test_dict.get("Cosmos", 0) - 1
    #             #             test_resource -= 1
    #             #     #Blob service, we only focus on Blob and container now
    #             #     elif (":10000" in rest):
    #             #         if "PUT" in rest and "status_code = 201" in rest and "Container" in rest:
    #             #             test_dict["Blob_Container"] = test_dict.get("Blob_Container", 0) + 1
    #             #             test_resource += 1
    #             #         elif "DELETE" in rest and "status_code = 202" in rest and "Container" in rest:
    #             #             test_dict["Blob_Container"] = test_dict.get("Blob_Container", 0) - 1
    #             #             test_resource -= 1
    #             #         elif "PUT" in rest  and "status_code = 201" in rest:
    #             #             test_dict["Blob"] = test_dict.get("Blob", 0) + 1
    #             #             test_resource += 1
    #             #         elif "DELETE" in rest and "status_code = 202" in rest:
    #             #             test_dict["Blob"] = test_dict.get("Blob", 0) - 1
    #             #             test_resource -= 1
    #             #     #Queue Service, we only focus on Queue and Message now. Actually, they are all service Azure Queue has now.
    #             #     elif (":10001" in rest):
    #             #         #situation of add one message
    #             #         if "POST" in rest and "status_code = 201" in rest and "messages" in rest:
    #             #             test_dict["Queue_Message"] = test_dict.get("Queue_Message", 0) + 1
    #             #             test_resource += 1
    #             #         #situation of delete one message
    #             #         elif "DELETE" in rest and "status_code = 204" in rest and "messages" in rest and "popreceipt = string-value" in rest:
    #             #             test_dict["Queue_Message"] = test_dict.get("Queue_Message", 0) - 1
    #             #             test_resource -= 1
    #             #         #situation of clear Queue Message
    #             #         elif "DELETE" in rest and "status_code = 204" in rest and "messages" in rest:
    #             #             test_resource -= test_dict.get("Queue_Message", 0)
    #             #             test_dict["Queue_Message"] = 0
    #             #         #situation of add one queue
    #             #         elif "PUT" in rest and "status_code = 201" in rest:
    #             #             test_dict["Queue"] = test_dict.get("Queue", 0) + 1
    #             #             test_resource += 1
    #             #         #situation of delete one queue
    #             #         elif "DELETE" in rest and "status_code = 204" in rest:
    #             #             test_dict["Queue"] = test_dict.get("Queue", 0) - 1
    #             #             test_resource -= 1
    #             #     #Table Service, we only focus on Table creation and deletion now.
    #             #     elif (":10002" in rest):
    #             #         if "POST" in rest and ("status_code = 201" or "status_code = 204") in rest and "Tables" in rest:
    #             #             test_dict["Table"] = test_dict.get("Table", 0) + 1
    #             #             test_resource += 1
    #             #         elif ("DELETE" in rest) and ("status_code = 204") in rest and "Tables" in rest:
    #             #             test_dict["Table"] = test_dict.get("Table", 0) - 1
    #             #             test_resource -= 1
    #         else:
    #             if (("PUT" in rest or "DELETE" in rest or "POST" in rest)) and \
    #                 (":8081" in rest or ":10000" in rest or ":10001" in rest or ":10002" in rest) and \
    #                 ("reason_phrase = Created" in rest or
    #                  "reason_phrase = No Content" in rest or
    #                  "reason_phrase = Accepted" in rest):
    #                  vanilla_list.append(rest)

    # with open(file_2, newline='') as injection_result:
    #     rows = csv.DictReader(injection_result, delimiter='\t')
    #     for row in rows:
    #         rest = row["REST"]
    #         if args.local:
    #             print("We have ditched the local resource leak check design")
    #             # if ("PUT" in rest or "DELETE" in rest or "POST" in rest) and \
    #             #     ("comp = lease" not in rest) and \
    #             #     ("/$batch" not in rest) and \
    #             #     ("status_code = 2" in rest):
    #             #     #Cosmos Service, we does not specify the exact resource of Cosmos now due to too many kinds of Cosmos service.
    #             #     if (":8081" in rest):
    #             #         if ("PUT" in rest or "POST" in rest) and "reason_phrase = Created" in rest:
    #             #             vanilla_dict["Cosmos"] = vanilla_dict.get("Cosmos", 0) + 1
    #             #             vanilla_resource += 1
    #             #         elif ("reason_phrase = No Content"):
    #             #             vanilla_dict["Cosmos"] = vanilla_dict.get("Cosmos", 0) - 1
    #             #             vanilla_resource -= 1
    #             #     #Blob service, we only focus on Blob and container now
    #             #     elif (":10000" in rest):
    #             #         if "PUT" in rest  and "status_code = 201" in rest and "Container" in rest:
    #             #             vanilla_dict["Blob_Container"] = vanilla_dict.get("Blob_Container", 0) + 1
    #             #             vanilla_resource += 1
    #             #         elif "DELETE" in rest and "status_code = 202" in rest and "Container" in rest:
    #             #             vanilla_dict["Blob_Container"] = vanilla_dict.get("Blob_Container", 0) - 1
    #             #             vanilla_resource -= 1
    #             #         elif "PUT" in rest and "status_code = 201" in rest:
    #             #             vanilla_dict["Blob"] = vanilla_dict.get("Blob", 0) + 1
    #             #             vanilla_resource += 1
    #             #         elif "DELETE" in rest and "status_code = 202" in rest:
    #             #             vanilla_dict["Blob"] = vanilla_dict.get("Blob", 0) - 1
    #             #             vanilla_resource -= 1
    #             #     #Queue Service, we only focus on Queue and Message now. Actually, they are all service Azure Queue has now.
    #             #     elif (":10001" in rest):
    #             #         #situation of add one message
    #             #         if "POST" in rest and "status_code = 201" in rest and "messages" in rest:
    #             #             vanilla_dict["Queue_Message"] = vanilla_dict.get("Queue_Message", 0) + 1
    #             #             vanilla_resource += 1
    #             #         #situation of delete one message
    #             #         elif "DELETE" in rest and "status_code = 204" in rest and "messages" in rest and "popreceipt = string-value" in rest:
    #             #             vanilla_dict["Queue_Message"] = vanilla_dict.get("Queue_Message", 0) - 1
    #             #             vanilla_resource -= 1
    #             #         #situation of clear Queue Message
    #             #         elif "DELETE" in rest and "status_code = 204" in rest and "messages" in rest:
    #             #             vanilla_resource -= vanilla_dict.get("Queue_Message", 0)
    #             #             vanilla_dict["Queue_Message"] = 0
    #             #         elif "PUT" in rest and "status_code = 201" in rest:
    #             #             vanilla_dict["Queue"] = vanilla_dict.get("Queue", 0) + 1
    #             #             vanilla_resource += 1
    #             #         elif "DELETE" in rest and "status_code = 204" in rest:
    #             #             vanilla_dict["Queue"] = vanilla_dict.get("Queue", 0) - 1
    #             #             vanilla_resource -= 1
    #             #      #Table Service, we only focus on Table creation and deletion now.
    #             #     elif (":10002" in rest):
    #             #         if "POST" in rest and ("status_code = 201" or "status_code = 204") in rest and "Tables" in rest:
    #             #             vanilla_dict["Table"] = vanilla_dict.get("Table", 0) + 1
    #             #             vanilla_resource += 1
    #             #         elif ("DELETE" in rest) and ("status_code = 204") in rest and "Tables" in rest:
    #             #             vanilla_dict["Table"] = vanilla_dict.get("Table", 0) - 1
    #             #             vanilla_resource -= 1
    #         else:
    #             if (("PUT" in rest or "DELETE" in rest or "POST" in rest)) and \
    #                 (":8081" in rest or ":10000" in rest or ":10001" in rest or ":10002" in rest) and \
    #                 ("reason_phrase = Created" in rest or
    #                  "reason_phrase = No Content" in rest or
    #                  "reason_phrase = Accepted" in rest):
    #                  test_list.append(rest)
    # print(test_dict)
    # print(vanilla_dict)
    # c_test_resource = Counter(test_dict)
    # c_vanilla_resource = Counter(vanilla_dict)
    # c_test_resource.subtract(c_vanilla_resource)
    # print(c_test_resource)
    # return (test_list == vanilla_list)
    return result

def select_from_resource_leak():
    
    output_dir_proj = os.path.join("../../results", args.round)
    test_dict = {}
    if args.local:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_local.csv")
    else:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_remote.csv")
    
    with open(bug_f_path, newline='') as leak_result:
        rows = csv.DictReader(leak_result, delimiter='\t')
        for row in rows:
            rest = row["Name"]
            test_dict[rest] = test_dict.get(rest, 0) + 1
    dup_list = [k for k, v in test_dict.items() if v >= 2]
    # print(dup_list)
    return dup_list

def check_random_test():
    dup_list = select_from_resource_leak()
    flaky_list = []
    for i in dup_list:
        test_dir_1 = os.path.join(vanilla_1_dir, i )
        test_dir_2 = os.path.join(vanilla_2_dir, i )
        # print(test_dir_1)
        # print(test_dir_2)

        rest_dir_1 = test_dir_1 + "\\0\\RESTAPI.csv"
        rest_dir_2 = test_dir_2 + "\\0\\RESTAPI.csv"
        # print(rest_dir_1)
        # print(rest_dir_2)
        try:
            status = compare(rest_dir_1, rest_dir_2)
        except:
            # flaky_list.append(i)
            status = False
            print(rest_dir_1)
            print(rest_dir_2)
            print("Cannot find files above")
        if not status:
            flaky_list.append(i)
    # print(flaky_list)
    # print("dup_list length = " + str(len(dup_list)) )
    # print("flaky_list length = " + str(len(flaky_list)) )
    
    output_dir_proj = os.path.join("../../results", args.round)
    if args.local:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_local.csv")
        tmp_output = os.path.join(output_dir_proj, "tmp_resource_leak_local.csv")
    else:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_remote.csv")
        tmp_output = os.path.join(output_dir_proj, "tmp_resource_leak_remote.csv")
    
    with open(bug_f_path, "r") as input:
        with open(tmp_output, "w") as output:
            for line in input:
                test_name = line.split("\t")[0]
                if test_name in flaky_list:
                    continue
                else:
                    output.write(line)
    os.replace(tmp_output, bug_f_path)
    # os.remove(tmp_output)

if __name__ == "__main__":
    # print(stat_dir)
    check_random_test()
