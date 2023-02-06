from msilib.schema import Directory
import pandas as pd
import xml.etree.ElementTree as ET
import os
import collections
import shutil
import argparse
import pathlib
from utils import find_latest_dir, create_test_run_result_dir


class OutcomeGenerator:
    num_of_file = 0
    num_of_test = 0

    pass_cnt = 0
    fail_cnt = 0
    skip_cnt = 0
    total_test_runs = 0

    pass_result_set = set()
    failed_result_set = set()
    skipped_result_set = set()
    all_tests_names_set = set()
    all_tests_names_list = []
    tests_result_dict = {}

    def __init__(self, _result_dir_str, _proj_name, _new_run_dir):
        self.result_dir_str = _result_dir_str
        self.directory = os.fsencode(_result_dir_str)
        self.proj_name = _proj_name
        self.new_run_dir = _new_run_dir

    def generate(self):
        for file in os.listdir(self.directory):
            test_dir_name = os.fsdecode(file)
            dir_str = self.result_dir_str + "/" + test_dir_name
            # print(dir_str)
            if os.path.isdir(dir_str):
                self.num_of_test += 1
                for path in os.listdir(dir_str):
                    num_file = []
                    result_file_path = os.path.join(dir_str, path)
                    if os.path.isfile(result_file_path):
                        self.num_of_file += 1
                        num_file.append(result_file_path)
                        # print(result_file_path)
                        tree = ET.parse(result_file_path)
                        root = tree.getroot()

                        if root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results') == None:
                            # If a test was blamed during running, it will not have Results leaf in XML
                            print("Blamed tests: {}".format(test_dir_name))
                            # So we need to use ResultSummary instead
                            child = root.find(
                                './/{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}ResultSummary')
                            self.all_tests_names_set.add(test_dir_name)
                            self.all_tests_names_list.append(test_dir_name)
                            if child.attrib.get('outcome') == "Passed":
                                self.pass_cnt += 1
                                self.pass_result_set.add(test_dir_name)
                                self.tests_result_dict[test_dir_name] = "Passed"
                            elif child.attrib.get('outcome') == "Failed":
                                self.fail_cnt += 1
                                self.failed_result_set.add(test_dir_name)
                                self.tests_result_dict[test_dir_name] = "Failed"
                            elif child.attrib.get('outcome') == "NotExecuted":
                                self.skip_cnt += 1
                                self.skipped_result_set.add(test_dir_name)
                                self.tests_result_dict[test_dir_name] = "Skipped"
                        else:
                            children = root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results')
                            for child in children:
                                # print(child.attrib.get('outcome'))
                                self.all_tests_names_set.add(test_dir_name)
                                self.all_tests_names_list.append(test_dir_name)
                                if child.attrib.get('outcome') == "Passed":
                                    self.pass_cnt += 1
                                    self.pass_result_set.add(test_dir_name)
                                    self.tests_result_dict[test_dir_name] = "Passed"
                                elif child.attrib.get('outcome') == "Failed":
                                    self.fail_cnt += 1
                                    self.failed_result_set.add(test_dir_name)
                                    self.tests_result_dict[test_dir_name] = "Failed"
                                elif child.attrib.get('outcome') == "NotExecuted":
                                    self.skip_cnt += 1
                                    self.skipped_result_set.add(test_dir_name)
                                    self.tests_result_dict[test_dir_name] = "Skipped"
                    if len(num_file) > 1:
                        print("Num of file under {} is larger than 1".format(dir_str))
        self.__print_output_stat()
        self.__write_output()
        self.__copy_f_to_result_dir()

    def __print_output_stat(self):
        self.total_test_runs = self.pass_cnt + self.fail_cnt + self.skip_cnt
        print("TOTAL # unit tests to run: {}".format(self.num_of_test))
        print("TOTAL # test rounds to run: {}".format(self.total_test_runs))
        print("# of files: {}".format(self.num_of_file))
        print("# PASSED tests: {}".format(self.pass_cnt))
        print("# FAILED tests: {}".format(self.fail_cnt))
        print("# SKIPPED tests: {}".format(self.skip_cnt))

    # Write outcome results to files.
    def __write_output(self):
        # Stat file output
        stat_file = open(self.new_run_dir + "/test-stats.txt", "w+")
        stat_file.write("TOTAL # unit tests to run: {}\n".format(self.num_of_test))
        stat_file.write("TOTAL # test rounds to run: {}\n".format(self.total_test_runs))
        stat_file.write("# PASSED tests: {}\n".format(self.pass_cnt))
        stat_file.write("# FAILED tests: {}\n".format(self.fail_cnt))
        stat_file.write("# SKIPPED tests: {}\n".format(self.skip_cnt))
        stat_file.close()

        # PASSED test output
        pass_file = open(self.new_run_dir + "/PASSED_test.csv", "w+")
        for ele in sorted(self.pass_result_set):
            pass_file.write("{}\n".format(ele))
        pass_file.close()

        # FAILED test output
        fail_file = open(self.new_run_dir + "/FAILED_test.csv", "w+")
        for ele in sorted(self.failed_result_set):
            fail_file.write("{}\n".format(ele))
        fail_file.close()

        # SKIPPED test output
        skip_file = open(self.new_run_dir + "/SKIPPED_test.csv", "w+")
        for ele in sorted(self.skipped_result_set):
            skip_file.write("{}\n".format(ele))
        skip_file.close()

        # all_test_observed_at_REST_layer output
        rest_df = pd.read_csv("test_CALLSITE.csv", sep="\t", header=None)
        rest_df.columns = ["TEST_NAME", "CALL_NUM"]
        rest_df = rest_df[rest_df["CALL_NUM"] != 0]
        rest_df["TEST_NAME"].to_csv(self.new_run_dir + "/all_test_observed_at_REST_layer.csv", header=False, index=False)

    # Copy the files to the destination result dir (name in lower case)
    def __copy_f_to_result_dir(self):
        for f in os.listdir(self.new_run_dir):
            src_file_path = os.path.join(self.new_run_dir, f)
            print(os.path.join(self.new_run_dir, f))
            dst_dir_path = os.path.join(self.new_run_dir, "..", self.proj_name)
            dst_file_path = os.path.join(self.new_run_dir, "..", self.proj_name, f)
            if_dir_exist = os.path.isdir(dst_dir_path)
            print(dst_dir_path, if_dir_exist)
            if not if_dir_exist:
                os.makedirs(dst_dir_path)
            shutil.copyfile(src_file_path, dst_file_path)
        # print("Redundant tests:")
        # print([item for item, count in collections.Counter(self.all_tests_names_list).items() if count > 1])

    def append_result_to_collection(self):
        one_round_result = pd.DataFrame.from_dict(self.tests_result_dict, orient='index', columns=["OUTCOME"])
        one_round_result['TEST_NAME'] = one_round_result.index

        one_round_result.reset_index(drop=True, inplace=True)
        # print(one_round_result)

        result_file = "~/rainmaker/results/" + self.proj_name + "/azure-test-outcomes.csv"
        prev_all_results = pd.read_csv(result_file, sep="\t")
        # print(prev_all_results)

        new_column_num = len(prev_all_results.columns)
        merged_left = pd.merge(left=prev_all_results, right=one_round_result, how='left', left_on='TEST_NAME',
                               right_on='TEST_NAME')
        new_col_name = "OUTCOME_" + str(new_column_num)
        merged_left = merged_left.rename(columns={'OUTCOME': new_col_name})
        # print(merged_left)

        merged_left[new_col_name].fillna("NotExecuted", inplace=True)
        merged_left.to_csv("~/rainmaker/results/" + self.proj_name + "/azure-test-outcomes.csv", sep="\t", index=False)

    def check_redundant_test(self):
        directory = os.fsencode(self.result_dir_str)
        all_tests_names_list = []
        for file in os.listdir(directory):
            test_dir_name = os.fsdecode(file)
            dir_str = self.result_dir_str + "/" + test_dir_name
            if os.path.isdir(dir_str):
                for path in os.listdir(dir_str):
                    result_file_path = os.path.join(dir_str, path)
                    if os.path.isfile(result_file_path):
                        # print(result_file_path)
                        tree = ET.parse(result_file_path)
                        root = tree.getroot()

                        if root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results') == None:
                            child = root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}ResultSummary')
                            all_tests_names_list.append(test_dir_name)
                        else:
                            for child in root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results'):
                                # print(child.attrib.get('outcome'))
                                all_tests_names_list.append(test_dir_name)
        print("Redundant tests:")
        print([item for item, count in collections.Counter(all_tests_names_list).items() if count > 1])

    def mv_failed_tests(self):
        fail_cnt = 0
        failed_result_set = set()
        tests_result_dict = {}

        failed_test_dir = "../../results/" + self.proj_name + "/failed_tests"
        if not os.path.isdir(failed_test_dir):
            os.mkdir(failed_test_dir)

        test_round_name = self.result_dir_str.split("/")[-1]
        failed_test_round_dir = "../../results/" + self.proj_name + "/failed_tests/" + test_round_name
        if not os.path.isdir(failed_test_round_dir):
            os.mkdir(failed_test_round_dir)

        for file in os.listdir(self.directory):
            test_dir_name = os.fsdecode(file)
            dir_str = self.result_dir_str + "/" + test_dir_name
            print(dir_str)
            if os.path.isdir(dir_str):
                for path in os.listdir(dir_str):
                    num_file = []
                    result_file_path = os.path.join(dir_str, path)
                    if os.path.isfile(result_file_path):
                        num_file.append(result_file_path)
                        # print(result_file_path)
                        tree = ET.parse(result_file_path)
                        root = tree.getroot()

                        for child in root.find('.//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}Results'):
                            # print(child.attrib.get('outcome'))
                            if child.attrib.get('outcome') == "Failed":
                                fail_cnt += 1
                                failed_result_set.add(test_dir_name)
                                tests_result_dict[test_dir_name] = "Failed"
                                # move to the failed test dir to ../../results/orleans/failed_tests
                                shutil.copytree(dir_str, failed_test_round_dir + "/" + test_dir_name)

                    if len(num_file) > 1:
                        print("Num of file under {} is larger than 1".format(dir_str))


if __name__ == "__main__":
    def_proj = "orleans"

    # Latest outcomes:
    def_directory = find_latest_dir("outcome")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=def_directory, help="The directory to run analysis")
    parser.add_argument("-p", "--proj", default=def_proj, help="The project to persist the results for")
    args = parser.parse_args()
    if args.dir != def_directory:
        tar_dir = "outcome/" + args.dir
    else:
        tar_dir = args.dir

    latest_outcome_dir = tar_dir
    # dir_name = return_latest_dir_name("outcome")
    dir_name = pathlib.PurePath(tar_dir).name
    latest_result_dir = create_test_run_result_dir(os.path.join("..", "..", "results"), dir_name)
    og = OutcomeGenerator(latest_outcome_dir, args.proj, latest_result_dir)
    og.generate()

    # check_redundant_test(latest_outcome_dir)

    # Move failed test dir to failed_tests
    # mv_failed_tests(latest_outcome_dir, args.proj)

    # Append test results to result file
    # append_result_to_collection(one_round_result_dict, args.proj)
