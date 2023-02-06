import datetime
import os
import pathlib
from collections import deque
  

def get_index_of_closing_bracket(s, i):
    if s[i] != '[':
        return -1
    d = deque()
    # Traverse through all elements starting from i.
    for k in range(i, len(s)):
        # Pop a starting bracket for every closing bracket
        if s[k] == ']':
            d.popleft()
        # Push all starting brackets
        elif s[k] == '[':
            d.append(s[i])
        # If deque becomes empty
        if not d:
            return k
    return -1


def return_time_stamps(proj_result_dir):
    # print(proj_result_dir)
    ts_list = []
    dir_ts_dict = {}
    for file in os.listdir(proj_result_dir):
        if file == ".DS_Store":
            continue
        # print(file)
        test_run_dir_name = os.fsdecode(file)

        # skip the results/orleans file when searching under results dirs
        if "_" not in test_run_dir_name:
            continue
        ts_str = test_run_dir_name.split("_")[1]
        ts = datetime.datetime.strptime(ts_str, "%Y.%m.%d.%H.%M.%S")
        ts_list.append(ts)
        dir_ts_dict[ts] = test_run_dir_name
    return ts_list, dir_ts_dict


def find_latest_dir(proj_result_dir):
    ts_list, dir_ts_dict = return_time_stamps(proj_result_dir)
    latest_ts = max(ts_list)
    latest_dir = proj_result_dir+"/"+dir_ts_dict[latest_ts]
    print("Latest dir: {}".format(latest_dir))
    return latest_dir


def find_second_latest_dir(proj_result_dir):
    ts_list, dir_ts_dict = return_time_stamps(proj_result_dir)
    ts_list.sort()
    sec_latest_ts = ts_list[-2]
    sec_latest_dir = proj_result_dir+"/"+dir_ts_dict[sec_latest_ts]
    print("Second latest dir: {}".format(sec_latest_dir))
    return sec_latest_dir


def find_third_latest_dir(proj_result_dir):
    ts_list, dir_ts_dict = return_time_stamps(proj_result_dir)
    ts_list.sort()
    third_latest_ts = ts_list[-3]
    third_latest_dir = proj_result_dir+"/"+dir_ts_dict[third_latest_ts]
    print("Third latest dir: {}".format(third_latest_dir))
    return third_latest_dir


def return_latest_dir_name(proj_result_dir):
    result_dir_str = find_latest_dir(proj_result_dir)
    return pathlib.PurePath(result_dir_str).name


def create_test_run_result_dir(path, result_dir_name):
    to_create_path = os.path.join(path, result_dir_name)
    isExist = os.path.exists(to_create_path)
    if not isExist:
        os.makedirs(to_create_path)
    return to_create_path


def transform_timing_into_seconds(runtime_str):
    if runtime_str.__contains__('m'):
        min_to_sec_time = float(runtime_str.split('m')[0]) * 60
        sec_time = float(runtime_str.split('m')[1].split('s')[0].lstrip())
        total_sec_time = min_to_sec_time + sec_time
    else:
        total_sec_time = float(runtime_str.split('s')[0].lstrip())

    return f"{total_sec_time:.3f}"


def read_test_running_time(file):
    # rainmaker/results/XXX/test_time.csv
    test_time_dict = dict()
    with open(file) as f:
        next(f)
        for line in f.readlines():
            # print(line)
            item = line.split(',')
            test_name = item[0]
            time = float(transform_timing_into_seconds(item[1]))
            test_time_dict[test_name] = time
    return test_time_dict


def sum_running_time(file):
    time_dict = read_test_running_time(file)
    total_time = datetime.timedelta(seconds=sum(time_dict.values()))
    print(total_time)


if __name__ == "__main__":
    sum_running_time('../../results/orleans/test_time.csv')

