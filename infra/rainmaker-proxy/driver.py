import os
import sys
import json
import subprocess
import argparse
from utils import find_latest_dir

config_alpakka = "repro-alpakka.json"
config_attachmentplugin = "repro-attachmentplugin.json"
config_botbuilder = "repro-botbuilder.json"
config_distributedlock = "repro-distributedlock.json"
config_efcore = "repro-efcore.json"
config_fhirserver = "repro-fhirserver.json"
config_insights = "repro-insights.json"
config_ironpigeon = "repro-ironpigeon.json"
config_orleans = "repro-orleans.json"
config_sleet = "repro-sleet.json"
config_storage = "repro-storage.json"

path_config = "artifacts/"

def_app = "botbuilder"
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--eval", default=def_app, help="The application going to be evaluated.")
parser.add_argument("-a", "--all", default=False, help="Run all of the test cases.")

args = parser.parse_args()

if args.eval == "alpakka":
    path_config = os.path.join(path_config, config_alpakka)
elif args.eval == "attachmentplugin":
    path_config = os.path.join(path_config, config_attachmentplugin)
elif args.eval == "botbuilder":
    path_config = os.path.join(path_config, config_botbuilder)
elif args.eval == "distributedlock":
    path_config = os.path.join(path_config, config_distributedlock)
elif args.eval == "efcore":
    path_config = os.path.join(path_config, config_efcore)
elif args.eval == "fhirserver":
    path_config = os.path.join(path_config, config_fhirserver)
elif args.eval == "insights":
    path_config = os.path.join(path_config, config_insights)
elif args.eval == "ironpigeon":
    path_config = os.path.join(path_config, config_ironpigeon)
elif args.eval == "orleans":
    path_config = os.path.join(path_config, config_orleans)
elif args.eval == "sleet":
    path_config = os.path.join(path_config, config_sleet)
elif args.eval == "storage":
    path_config = os.path.join(path_config, config_storage)
else:
    path_config = os.path.join(path_config, config_botbuilder)

f = open(path_config)

home_dir = os.path.expanduser('~')
rainmaker_ps = os.path.join(home_dir, "rainmaker\\infra\\rainmaker-proxy\\rainmaker.ps1")

objects = json.load(f)
for obj in objects:
    if not obj['skip']:
        project = obj['project']
        policy = 'vanilla'
        configs = []

        # Reference round
        if obj['policy'] == 'vanilla':
            configs.append(obj)
            out = json.dumps(configs)
            with open("config_generated.json", "w") as outf:
                outf.write(out)
                # json.dump(obj, open("config_generated.json","w"))
            p = subprocess.Popen(["powershell.exe", rainmaker_ps], stdout=sys.stdout)
            p.communicate()
        else:
            policy = obj['policy']
            obj['policy'] = 'vanilla'
            print(obj)
            configs.append(obj)
            out = json.dumps(configs)
            with open("config_generated.json", "w") as outf:
                outf.write(out)
                # vanilla_stat = find_latest_dir("stat")
            # obj['stat_dir'] = vanilla_stat.replace('/', '\\')
            # json.dump(obj, open("config_generated.json","w"))
            p = subprocess.Popen(["powershell.exe", rainmaker_ps], stdout=sys.stdout)
            p.communicate()

        # Reference round - collect vanilla result
        # stat_directory     = find_latest_dir("stat")
        # raw_stat_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
        # outcome_directory  = find_latest_dir("outcome")
        open('driver-1.txt', 'w').close()
        os.system("python ./test_all.py")

        # Testing round
        if policy != 'vanilla':
            obj['policy'] = policy
            configs = []
            vanilla_stat = find_latest_dir("stat")
            obj['stat_dir'] = vanilla_stat.replace('/', '\\')
            configs.append(obj)
            out = json.dumps(configs)
            with open("config_generated.json", "w") as outf:
                outf.write(out)
            p = subprocess.Popen(["powershell.exe", rainmaker_ps], stdout=sys.stdout)
            p.communicate()

            # Investigation round
            stat_directory = find_latest_dir("stat")
            raw_stat_directory = find_latest_dir(os.path.join(os.getcwd(), "stat"))
            outcome_directory = find_latest_dir("outcome")
            print(project)
            open('driver-2.txt', 'w').close()
            print("python ./test_all.py -p " + project + " -s " + stat_directory    \
                + " -r " + raw_stat_directory + " -o " + outcome_directory + " 1>>driver.txt")
            # os.system("python ./test_all.py -p " + project + " -s " + stat_directory \
            #           + " -r " + raw_stat_directory + " -o " + outcome_directory + " 1>>driver.txt")
            os.system("python ./test_raw_data_generator.py -d " + raw_stat_directory + "  -u False 1>>driver.txt")
            os.system("python ./test_stat_generator.py -d " + stat_directory + " -p " + project + " -u False 1>>driver.txt")
            os.system("python ./test_outcome_generator.py -d " + outcome_directory + " -p " + project + " 1>>driver.txt")

            round = os.path.basename(os.path.normpath(stat_directory))
            os.system("python ./check_injection_result.py -v " + vanilla_stat + " -r " + round \
                      + " -p " + project + " -P " + policy + " 1>>driver.txt")

