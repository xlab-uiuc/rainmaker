import os.path
import argparse
from pathlib import Path

descp = "This is the coverage finder of Rainmaker to calculate the fault injection SDK API coverage.\nFor example, you can use it in this way to start your coverage calculation:\n\tpython3 coverage_finder.py --project PROJECT_PATH\n" 

# def_proj_path = os.path.join(Path.home(), "orleans\\src\\Azure")

# def_proj_path = os.path.join(Path.home(), "botbuilder-dotnet\\libraries\\Microsoft.Bot.Builder.Azure")
def_proj_path = os.path.join(Path.home(), "storage\\src\\Azure")

parser = argparse.ArgumentParser(
    description=descp, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--project", "-p", default=def_proj_path,
                    help="Project path for coverage calculation")

args = parser.parse_args()

prefix_keywords = ["Azure.Data.Tables.TableClient", "Azure.Data.Tables.TableServiceClient",
    "Azure.Data.Tables.TableRestClient", "Azure.Storage.Queues.QueueClient", "Azure.Storage.Blobs.BlobClient",
    "Azure.Storage.Blobs.BlobContainerClient", "Azure.Storage.Blobs.Specialized.BlobBaseClient"]

exclude_apis = ["TableServiceClient.GetTableClient", "TableClient.CreateQueryFilter", 
    "BlobContainerClient.GetBlobClient", ".EventHubs.", "Orleans.Transactions.", "Orleans.Streaming.AzureStorage."]
#  ["TableServiceClient.GetTableClient", "TableClient.CreateQueryFilter", 
#     "BlobContainerClient.GetBlobClient"]

def find_coverage():
    with open("raw_cov_result.txt", "w+") as f:
        f.close()
    for dir_path, dir_names, filenames in os.walk(args.project):
        for filename in [f for f in filenames if f.endswith(".dll")]:
            # if "\\bin\\Debug\\net5.0" in dir_path:
            if "\\bin\\Debug\\netstandard2.0" in dir_path:
                with open("raw_cov_result.txt", "a") as f:
                    for prefix in prefix_keywords:
                        target_path = os.path.join(dir_path, filename)
                        cmd = ".\\CallFinder.exe " + target_path + " " + prefix
                        pipeline = os.popen(cmd)
                        read = pipeline.read() 
                        f.write(target_path+"\n")
                        f.write(read)
                        print(target_path)
                        print(read)


def filter_results():
    # api_set = set()
    # with open("raw_cov_result.txt", "r") as f:
    #     for line in f.readlines():
    #         if "MethodCall:" in line and "#MethodCall:" not in line:
    #             if ".get_" not in line:
    #                 # Exclude API that will not send request
    #                 if all(x not in line for x in exclude_apis):
    #                     if "`" in line:
    #                         elements = line.split("`1")
    #                         print(line)
    #                         api_set.add(elements[1])
    #                     else:    
    #                         elements = line.split("/<")
    #                         print(line)
    #                         api_set.add(elements[1])
    # f.close()

    # with open("cov_result.txt", "w") as out_f:
    #     for ele in api_set:
    #         out_f.write(ele)
    # out_f.close()

    with open("raw_cov_result.txt", "r") as f:
        with open("cov_result.txt", "w") as out_f:
            for line in f.readlines():
                if "MethodCall:" in line and "#MethodCall:" not in line:
                    if ".get_" not in line:
                        # Exclude API that will not send request
                        if all(x not in line for x in exclude_apis):
                            out_f.write(line)
        out_f.close()
    f.close()
                    
                    
if __name__ == "__main__":
    find_coverage()
    filter_results()
