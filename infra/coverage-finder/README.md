## Introduction

This is the API coverage finder of Rainmaker to calculate the fault injection SDK API coverage.

Note: this is not related to the coverage metrics supported by Rainmaker. 


## Usage

#### Command

You need to specify the project production source code path(different from test code path in config.json) by using `-p` argument when running `coverage_finder.py`, e.g., `python3 coverage_finder.py --project PROJECT_PATH`. The result APIs will be written to the file `cov_result.txt` in the `coverage-finder` folder.

#### Heuristics

There are two global arrays in the code which are `prefix_keywords` and `exclude_apis`. The current version is for evaluating Orleans, you may want to change this if you are evaluating a different application. The `prefix_keywords` specifies the keywords you want to find in target APIs, e.g., `Microsoft.Azure.Storage.Blob.CloudBlob`. On the contrary, the `exclude_apis` specifies the keywords you want to exclude for the APIs. For example, if you want to exclude the constructor functions, you can add `"..ctor"` into this array.

#### Target path

The target path is specified in [this line](https://github.com/xlab-uiuc/rainmaker/blob/37e0aa5ec82cdc12a275d98a807f1ca103d478a4/infra/coverage-finder/coverage_finder.py#L32). You **should check the dotnet version** that the application is using, and change the path accordingly. You can try different paths like `\\obj\\Debug\\DOTNET_VERSION` if there are no satisfying results under the `\\bin\\Debug\\DOTNET_VERSION` folder.

