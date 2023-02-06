from utils import return_latest_dir_name
import os
import csv
import argparse

descp = "This is resource leak file generator"

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
parser.add_argument("--local", "-l", default = def_local,
                    help="True for local resource test and False for remote resource test")
args = parser.parse_args()

stat_dir = os.path.join("stat", args.round)

def cmp_outcome():
    output_dir_proj = os.path.join("../../results", args.round)
    
    if args.local:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_local.csv")
        output_file = os.path.join(output_dir_proj, "Pruned_resource_leak_local.csv")
    else:
        bug_f_path = os.path.join(output_dir_proj, "resource_leak_remote.csv")
        output_file = os.path.join(output_dir_proj, "Pruned_resource_leak_remote.csv")

    f = open(output_file, "w", encoding="utf-8")
    f.write("Name\tTurn\tLeak\n")

    with open(bug_f_path, newline='') as injection_result:
        rows = csv.DictReader(injection_result, delimiter='\t')
        for row in rows:
            test_name = row["Name"]
            test_round = row["Turn"]
            leak_info = row["Leak"]
            pass_test_name = "test-result-" + test_round +"-0.trx"
            outcome_dir = os.path.join("./outcome", args.round) + "/" + test_name
            file_name_list = os.listdir(outcome_dir)
            if(pass_test_name in file_name_list):
                f.write("{}\t{}\t{}\n".format(test_name, test_round,leak_info))

    f.close()

if __name__ == "__main__":
    cmp_outcome()
    