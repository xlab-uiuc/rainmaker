import os
import argparse
from utils import return_latest_dir_name, find_latest_dir

#if not default, add stat/before the name

# TODO: make all these configurable 
# Based on the config.json file => automatically set these up

# proj = "servicestack"
# proj = "distributedlock"
# proj = "efcore"
# proj = "storage"
# raw_stat_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
# raw_stat_directory = "servicestack-injection-round_2022.07.19.23.43.15"
# raw_stat_directory = "fhir-server-injection-round_2022.08.15.09.50.01"

# stat_directory = find_latest_dir("stat")
# stat_directory = "fhir-server-injection-round_2022.08.15.09.50.01"
# stat_directory = "efcore-injection-round_2022.08.05.14.48.12"

# outcome_directory = find_latest_dir("outcome")
# outcome_directory = "efcore-injection-round_2022.08.05.14.48.12"
# outcome_directory = "fhir-server-injection-round_2022.08.15.09.50.01"

# For efcore
# proj = "efcore"
# raw_stat_directory = "efcore_2022.08.04.20.55.22"
# stat_directory = "efcore_2022.08.04.20.55.22"
# outcome_directory = "efcore_2022.08.04.20.55.22"

# For Botbuilder-dotnet vanilla
# proj = "botbuilder-dotnet"
# raw_stat_directory = "Botbuilder-dotnet_2022.05.06.06.00.32"
# stat_directory = "Botbuilder-dotnet_2022.05.06.06.00.32"
# outcome_directory = "Botbuilder-dotnet_2022.05.06.06.00.32"

# For Botbuilder-dotnet timeout injection 
# proj = "botbuilder-dotnet"
# stat_directory = "Botbuilder-dotnet-injection-round-500timeout_2022.05.06.06.33.24"
# stat_directory = "Botbuilder-dotnet-injection-round-503Req_2022.05.09.07.09.34"
# stat_directory = "Botbuilder-dotnet-injection-round_2022.08.24.02.50.35"
# stat_directory = "Botbuilder-dotnet-injection-round_2022.08.31.20.53.09"

# For DistributedLock
# proj = "distributedlock"
# raw_stat_directory = "DistributedLock_2022.05.13.05.29.54"
# stat_directory = "DistributedLock_2022.05.13.05.29.54"
# outcome_directory = "DistributedLock_2022.05.13.05.29.54"
# stat_directory = "DistributedLock-injection-round_2022.05.13.14.59.00"
# stat_directory = "DistributedLock-injection-round_2022.05.14.21.16.36"
# stat_directory = "DistributedLock-injection-round_2022.08.18.23.03.07"
# stat_directory = "DistributedLock-injection-round_2022.08.19.20.53.36"

# raw_stat_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
# stat_directory = find_latest_dir("stat")
# outcome_directory = find_latest_dir("outcome")

# policy = "timeout_injection"
# round = return_latest_dir_name("stat")
# vanilla_round = "TableStorage.Abstractions_2022.06.19.20.35.16"


if __name__ == "__main__":
    proj               = "Orleans"
    stat_directory     = find_latest_dir("stat")
    raw_stat_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
    outcome_directory  = find_latest_dir("outcome")

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--proj", default = proj, help="Project")
    parser.add_argument("-s", "--stat_directory", default = stat_directory, help="")
    parser.add_argument("-r", "--raw_stat_directory", default = raw_stat_directory, help="")
    parser.add_argument("-o", "--outcome_directory", default = outcome_directory, help="")
    args = parser.parse_args()

    open('log.txt', 'w').close()
    # -u is for PUT
    os.system("python ./test_raw_data_generator.py -d " + args.raw_stat_directory + "  -u False 1>>log.txt")
    # os.system("python ./test_raw_data_generator.py  1>>log.txt")

    os.system("python ./test_stat_generator.py -d " + args.stat_directory + " -p " + args.proj + " -u False 1>>log.txt")
    # os.system("python ./test_stat_generator.py 1>>log.txt")

    os.system("python ./test_outcome_generator.py -d " + args.outcome_directory + " -p " + args.proj + " 1>>log.txt")
    # os.system("python ./test_outcome_generator.py 1>>log.txt")
    
    
    