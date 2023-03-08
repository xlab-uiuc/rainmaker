# Rainmaker Infrastructure

Rainmaker aims to build a large-scale cloud application bug finding infrastructure.

**Warning: You have to put rainmaker & cloud application repos under the path "C:\Users\XX" to run rainmaker successfully. This problem will be fixed in the future.**

## Environment Setup before Using Rainmaker Proxy

### .NET

The .NET version should be decided by the cloud application under test. In most cases we recommend is .NET 6.0 since it is backward compatible.

To check .NET SDK: Go to C:\Program Files\dotnet\sdk to view all .NET SDK editions.

If you do not have .NET SDK, please go to [Download .NET](https://dotnet.microsoft.com/en-us/download/dotnet) to download and install.

### Maven

Install Java and Maven.

Java/Maven versions being tested (output from ``mvn -v``):

```
Apache Maven 3.8.4 (9b656c72d54e5bacbed989b64718c159fe39b537)                   
Java version: 11.0.14.1, vendor: Amazon.com Inc., runtime: XXX\.jdks\corretto-11.0.14.1
OS name: "windows 10", version: "10.0", arch: "amd64", family: "windows"
```

Java version: 11

### Python

Install Python3 and following packages in your system:

```
pandas
```

### Azure Storage settings

Rainmaker proxy will listen on ``127.0.0.1:10000,10001,10002`` which are default Azure Blob, Queue, Table storage services' ports respectively, and serve as a proxy to forward requests to ``127.0.0.1:20000,20001,20002`` correspondingly.

### If using Azurite (Recommended)

Azurite is the latest storage emulator platform. Azurite supersedes the [Azure Storage Emulator](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-emulator). Azurite will continue to be updated to support the latest versions of Azure Storage APIs. The reason why we use both Azurite and Azure Storage settings is that some frameworks we tested do not support Azurite.

#### Install Azurite:

Azurite is automatically available with [Visual Studio 2022](https://visualstudio.microsoft.com/vs/). If you are running an earlier version of Visual Studio, you'll need to install Azurite by using either Node Package Manager, DockerHub, or by cloning the Azurite github repository.

Reference: https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio

#### Run Azurite:

**Shortcut:** If you are using Visual Studio 2022, you can directly run `.\emulator.ps1` in PowerShell

Manually setup in PowerShell:

1. Go to Azurite executable's directory, e.g., ``cd 'C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\Extensions\Microsoft\Azure Storage Emulator'``
2. Since Azurite will automatically listen to 10000, 10001, 10002 of localhost, it is necessary to let it switch to other ports, i.e., ``.\azurite.exe --blobPort 20000 --queuePort 20001 --tablePort 20002``


**Warning:**
The emulator.ps1 should be run as admin 

reference: https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio

##### Caveat for Azurite:

If you want to run tests without Rainmaker, do not listen to ports 20000, 20001 and 20002, i.e.,  `.\azurite.exe`

### If using legacy Azure Storage Emulator (Not Recommended)

Since Azure Storage Emulator will automatically listen to 10000, 10001, 10002 of localhost, it is necessary to modify the ports configuration in ``AzureStorageEmulator.exe.config`` file under ``C:\Program Files (x86)\Microsoft SDKs\Azure\Storage Emulator`` directory:

```
<services>
  <service name="Blob" url="http://127.0.0.1:20000/"/>
  <service name="Queue" url="http://127.0.0.1:20001/"/>
  <service name="Table" url="http://127.0.0.1:20002/"/>
</services>
```

## Turn on the dynamic instrumentation tool

The instrumentation tool in our infra aims to capture the stack trace of the Azure Storage operations, and attach it to the corresponding request.

1. Open a PowerShell with Administrator permission (right click the PowerShell icon in Start menu, and select "Run as Administrator")
2. Go into Rainmaker infra dir
3. ``cd torch-tool``
4. Use ``.\ProfOn.ps1`` to turn on the dynamic instrumentation profiler
5. Since the environment settings of a PowerShell is established at the beginning of its life cycle, you should open another PowerShell with Administrator permission, and then the instrumentation will work
6. When finishing the instrumentation, use ``.\ProfOff.ps1`` to turn the profiler off. Notice that the instrumentation will still happen for the current shell, so remember to close it if you stop the instrumentation immediately

## How to use Rainmaker Proxy

**Shortcut:** `.\rainmaker.ps1`

The shortcut now will only run the step 1, 2 and 3 below.

Detailed steps: Modify the *config.json* file to configure the target projects, if a project should be skipped, then its corresponding "skip" field should be set to ``true``; then:

1. ``cd rainmaker-proxy``
2. ``mvn package``
3. ``java -jar .\target\rainmaker-proxy-1.0-SNAPSHOT.jar -Xmx8g``

``-Xmx8g`` is used to improve the JAVA heap memory

## How to collect the test results and generate the outcome

**Shortcut:** `.\test_all.ps1`

1. ``python test_raw_data_generator.py`` to generate API/Callsite files and beautified request JSON file

- Files will be generated for each test round under ``rainmaker/infra/rainmaker-proxy/stat/TESTRUN_TIMESTAMP/TESTROUND/``: b_request.json (beautified request JSON file), CALLSITE.csv (stat of callsite), RESTAPI.csv (stat of patterns of RESTful APIs), SDKAPI (stat of SDK APIs), overview.txt (overview file describing the running time etc.)
- The function `find_latest_dir` automatically finds the latest folder under `rainmaker-proxy/outcome` for analyzing , but you can also specify the tested folder manually by adding `-d` or `--dir` and the name of the target folder, e.g., `python .\test_raw_data_generator.py -d Orleans_2022.05.17.21.22.29`.

2. ``python test_stat_generator.py`` to generate statistic files constructing mappings from test to APIs/Callsites

- Files will be generated for each test round under ``rainmaker/results/PROJECTNAME/``: CALLSITE.csv (mapping from callsite to tests, i.e., for each callsite which test will exercise it), REST_API.csv (mapping from RESTful API pattern to tests), SDK_API.csv (mapping from SDK API to tests), test_API_stats.csv (overview stat of all types of APIs/Callsite and test running time), test_CALLSITE.csv (number of callsites for each test), test_REST_API.csv (number of RESTful API patterns for each test), test_SDK_API.csv (number of SDK APIs for each test), test_time.csv, test_uniq_CALLSITE.csv (number of unique callsites for each test), test_uniq_REST_API.csv (number of unique RESTful API patterns for each test), test_uniq_SDK_API.csv (number of unique SDK APIs for each test)

3. ``python test_outcome_generator.py`` to generate outcome files that collect passed, failed and skipped files into different places

- Files will be generated for each test round under ``rainmaker/results/PROJECTNAME/``: FAILED_test.csv (list of failed test names), PASSED_test.csv (list of succeeded test names), SKIPPED_test.csv (list of skipped test names), test-stats.txt

4. ``python check_injection_result.py`` to generate raw inspection file and apply two heuristics to test failures. Store the result in ``alarms`` folder. Please specify the project-related arguments: ``-p`` for project name, ``-v`` for vanilla round to refer to, ``-P`` for the injection policy used, ``-r`` for injection round dir (default is the latest injection)   **This step is not needed if you run the vanilla test.** You can check unique test failures with different pair of sdk and stacktrace in unique_bug_inspection.csv in result folder. We need run other policy first and later run keep_boring policy.

~~5. ``python bug_inspection_creator.py`` to generate inspection file in ``rainmaker/results/PROJECT`` folder. **This step is not needed if you run the vanilla test.**~~

## How to find out possible resource leak
(Need to automate these steps)
1. ``python test_all.py`` to generate resource file we need, like RESTAPI.csv.
2. ``python check_resource_leak.py`` to generate resource_leak_XXX.csv in the injected round result folder.
3. ``python prep_check_random.py`` to fill the partial test in config.json and we need to manually run rainmaker to get another vanilla round of partial tests.
4. ``python test_all.py`` to generate resource file we need for new partial vanilla round, like RESTAPI.csv.
5. ``python check_random_test.py`` to remove all random resource tests in the resource_leak_XXX.csv
6. ``python compare_two_oracle.py`` to remove tests that also can be found by our previous design.

#### We need to specify the def_XXX in all python script above. 

## Attach Visual Studio debugger to the test

If you want to attach VS debugger to the test, all you need to do is to set the value of a environment variable ``VSTEST_HOST_DEBUG`` to 1.

### Attach when using Rainmaker infra

If you want to use Rainmaker infra at the same time debugging the test, you should add a new variable named ``VSTEST_HOST_DEBUG`` with value set to 1 in System variables via Windows' adavanced system setting GUI. Then open a new Powershell since Powershell will only update its environment varaible at the beginning of its life cycle. Note that if you run in a IntelliJ terminal, you may need to restart IntelliJ.

After setting the variable properly, you should see this when you run Rainmaker:

```
Host debugging is enabled. Please attach debugger to testhost process to continue.
Process Id: 40244, Name: testhost
```

### Attach debugger without Rainmaker

If you are solely running a test and want to debug it (maybe using Fiddler at the same time), an easier way to do is to type ``$env:VSTEST_HOST_DEBUG=1`` in the current Powershell.

## Tips for monitoring the on-going tests

Use this command to know the current Nth running test: ``(Get-ChildItem -Directory | Measure-Object).Count``

## Caveat

- When you are going to analyze a new cloud-backed application, please always remember to turn on the Torch tool. E.g., when analyzing a project A from GitHub, remember to turn off and on Torch tool after git clone A.
- You may need to make a global.json file to specify the .NET version at the root of the cloud application repo.

### Caveat for AWS S3/SQS cloud applications
(How to automate this step?)
1. Add the MockServer certificate to the machine:
  - reference for adding certificate: https://support.securly.com/hc/en-us/articles/360026808753-How-do-I-manually-install-the-Securly-SSL-certificate-on-Windows
  - Mockserver certificate (PEM file): https://raw.githubusercontent.com/mock-server/mockserver/master/mockserver-core/src/main/resources/org/mockserver/socket/CertificateAuthorityCertificate.pem
2. Open the Windows system proxy on port 18081, IP 127.0.0.1 (Is it possible to automate this?)

### Caveat for Orleans project

**Shortcut:**(Must be done before running `rainmaker.ps1`)

1. copy [the file](https://github.com/xlab-uiuc/rainmaker/blob/main/patches/Orleans_patch_file.patch) into the base folder of orleans
2. `cd orleans`
3. `git apply .\Orleans_patch_file.patch`

Detailed steps of the shortcut above:

- Add the connection string ``"UseDevelopmentStorage=true"`` to the repo: you can add a line after [this line](https://github.com/dotnet/orleans/blob/14bc87740e830342a9eafb2e8e057794d7b7156c/test/TestInfrastructure/TestExtensions/TestDefaultConfiguration.cs#L67), i.e.,

```
{ nameof(ZooKeeperConnectionString), "127.0.0.1:2181" },
{ nameof(DataConnectionString), "UseDevelopmentStorage=true" }
```

- Orleans directly check the existence of the Azure Storage Emulator, so if you choose to use Azurite, you could comment out these [lines](https://github.com/dotnet/orleans/blob/3895e070ea4b9870440a5c44eed93262923b73a5/test/TestInfrastructure/TestExtensions/TestUtils.cs#L41-L46) before running the rainmaker proxy.

### Other caveats

1. When running the reference round, it is recommended to run reference test with internet disconnected to avoid some unrelated traffic.
2. When running the injection round in PowerShell, it is recommended to disable the "Quick Edit" feature of PowerShell to avoid the risk of accidental pause led by the bug of PowerShell.
3. (Optional) Changing Orleans timeout: #127
4. If you are using non-English language win10 platform for rainmaker, you should change Language for non-Unicode programs into English.


## Config

### Introduction:

 | Entry name                                         | Explanation                                        | Example                                                                                                                                                                                                                                                                                                                                                                                               |
 | :------------------------------------------------- | :------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
 | `project`                                        | Name of application                                | "Orleans"                                                                                                                                                                                                                                                                                                                                                                                             |
 | `project_test_path`                              | Application Test Unit path                         | "orleans\test\Extensions\TesterAzureUtils"                                                                                                                                                                                                                                                                                                                                                            |
 | `project_path_root`                              | Application root path to find application          | "\\Users\\"                                                                                                                                                                                                                                                                                                                                                                                           |
 | `rainmaker_path`                                 | Rainmaker project path to find rainmaker for test  | "rainmaker\\infra\\rainmaker-proxy"                                                                                                                                                                                                                                                                                                                                                                   |
 | `torch_path`                                     | Torch path to find torch dynamic instrumental tool | "rainmaker\\infra\\torch-tool"                                                                                                                                                                                                                                                                                                                                                                        |
 | `skip`                                           | Whether we choose to test this application         | true means do not test this application; false means test this application.                                                                                                                                                                                                                                                                                                                           |
 | `policy`                                         | Fault injection policy                             | "timeout_injection"                                                                                                                                                                                                                                                                                                                                                                                   |
 | `policies(for doc purpose)`                      | Fault injection policies for selection             | ["vanilla","timeout_injection (need to mod sleepTime>100)", "request_block"]                                                                                                                                                                                                                                                                                                                          |
 | `test_dll`                                       | Test_dll path to find application dll              | "%HOMEDRIVE%%HOMEPATH%\\orleans\\test\\Extensions\TesterAzureUtils\\bin\\Debug\\net5.0\\Tester.AzureUtils.dll"                                                                                                                                                                                                                                                                                        |
 | `test`                                           | we choose the partial test mode                    | false means No, true means Yes.                                                                                                                                                                                                                                                                                                                                                                       |
 | `full_test_or_vanilla`                           | Whether we choose the whole test mode              | false means No, true means Yes.                                                                                                                                                                                                                                                                                                                                                                       |
 | `partial_test`                                   | The partial test we run                            | ["Tester.AzureUtils.Streaming.AQProgrammaticSubscribeTest. StreamingTests_Consumer_Producer_SubscribeToStreamsHandledByDifferentStreamProvider"]                                                                                                                                                                                                                                                      |
 | `other_usually_used_tests(for doc purpose)`      | The partial test we usually choose                 | ["Tester.AzureUtils.TimerTests.ReminderTests_AzureTable.Rem_Azure_Wrong_Grain", "Tester.AzureUtils.Streaming.AQStreamingTests.AQ_01_OneProducerGrainOneConsumerGrain", "UnitTests.Streaming.Reliability.StreamReliabilityTests.AQ_StreamRel_SiloRestarts_Consumer", "Tester.AzureUtils.AzureQueueDataManagerTests.AQ_Standalone_1", "Tester.AzureUtils.AzureTableGrainDirectoryTests.LookupNotFound"] |
 | `stat_dir`                                       | stat for analysis directory path                   | "stat\\Orleans_2022.02.25.00.09.00"                                                                                                                                                                                                                                                                                                                                                                   |
 | `validation`                                     | Whether we choose the partial validation mode      | false means No, true means Yes.                                                                                                                                                                                                                                                                                                                                                                       |
 | `full_validation`                                | Whether we choose the full validation mode         | false means No, true means Yes.                                                                                                                                                                                                                                                                                                                                                                       |
 | `validation_round`                               | Validation round                                   | 1                                                                                                                                                                                                                                                                                                                                                                                                     |
 | `partial_validation`                             | The partial validation we run                      | ["Tester.AzureUtils.Streaming.AQStreamingTests.AQ_01_OneProducerGrainOneConsumerGrain"]                                                                                                                                                                                                                                                                                                               |
 | `other_usually_used_validation(for doc purpose)` | The validation we usually choose                   | ["Tester.AzureUtils.Persistence.PersistenceGrainTests_AzureTableGrainStorage.Grain_AzureTableGrainStorage_Read"]                                                                                                                                                                                                                                                                                      |

