# This file is to pick up multiple occur testname in resource_leak_xxx.csv and
from utils import return_latest_dir_name
import json
import os
import csv
import argparse

descp = "This is prepare partial test of resource leak checking results"

def_proj = "Insights"
# def_proj = "Orleans"
def_round = "Insights-injection-round-status-code_2022.09.02.12.45.19"
# def_round = "Orleans-injection-round-blind-all-true_2022.08.21.01.13.39"
# return_latest_dir_name("stat")
# def_vanilla_round = "Insights_2022.08.24.09.54.57"
# True for local resource check, and false for remote resource check
def_local = False

parser = argparse.ArgumentParser(
    description=descp, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--round", "-r", default=def_round,
                    help="The injection round (normally should be the latest one with timestamp)")
parser.add_argument("--project", "-p", default=def_proj,
                    help="The project name")
parser.add_argument("--local", "-l", default=def_local,
                    help="True for local resource test and False for remote resource test")
args = parser.parse_args()

stat_dir = os.path.join("stat", args.round)

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

def prep_check_random():
    with open('config.json') as f:
        config = json.load(f)
        for j_ele in config:
            if ('project' in j_ele) and (j_ele['project'] == args.project) and ('partial_test' in j_ele):
                j_ele['partial_test'] = select_from_resource_leak()
            else:
                continue
    with open('config.json', 'w') as f:
        json.dump(config, f, indent = 2)

if __name__ == "__main__":
    prep_check_random()
