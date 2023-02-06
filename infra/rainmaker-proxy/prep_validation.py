import json
import os
import csv

def prep_partial_validation():
    with open('config.json') as f:
        config = json.load(f)
    partial_data = []
    for j_ele in config:
        # if ('skip' in j_ele) and (j_ele['skip'] == 'False') and ('partial_validation' in j_ele):
        if ('skip' in j_ele) and (j_ele['skip'] == False) and ('validation' in j_ele and j_ele['validation'] == True and 'full_validation' in j_ele and j_ele['full_validation'] == False):
            print("The repo we plan to do partial validation is " + j_ele['project'])
            validation_proj_dir = os.path.abspath(os.path.join(os.getcwd(),"../..")) + "/results/" + j_ele['project'].lower() + "/bug_inspection.csv"
            print(validation_proj_dir)
            if("partial_validation_stat" in j_ele and len(j_ele['partial_validation_stat']) > 0):
                bug_inspection_dir = os.path.abspath(os.path.join(os.getcwd(),"../..")) + "/results/" + j_ele['partial_validation_stat'] + "/bug_inspection.csv"
                print(bug_inspection_dir)
               
                if("partial_validation" in j_ele):
                    with open(bug_inspection_dir, newline='') as injection_result:
                        rows = csv.DictReader(injection_result, delimiter='\t')
                        for row in rows:
                            if row['name'] in j_ele['partial_validation']:
                                partial_data.append("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                                row['name'], row['turn'], row['URI'], row['SDK'], row['policy'], row['outcome'], row['time'], 
                                row['excp_type'], row['heuristic1'], row['heuristic2'], row['bug?'],row['bug_ID'],row['bug_link']))
                            else:
                                continue
            else:
                 print("Need partial validation stat")
            
            f = open(validation_proj_dir, "w", encoding="utf-8")
            f.write("name\tturn\tURI\tSDK\tpolicy\toutcome\ttime\texcp_type\theuristic1\theuristic2\tbug?\tbug_ID\tbug_link\n")
            for i in partial_data:
                f.write(i)
            f.close
        else:
            continue
if __name__ == "__main__":
    prep_partial_validation()