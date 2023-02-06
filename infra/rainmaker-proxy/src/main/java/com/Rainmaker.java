package com;

import com.policies.*;

import org.json.JSONArray;
import org.json.JSONObject;
import org.apache.commons.lang3.StringUtils;

import org.mockserver.model.Format;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.configuration.ConfigurationProperties;
import static org.mockserver.model.HttpClassCallback.callback;
import static org.mockserver.model.HttpRequest.request;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import static java.nio.charset.StandardCharsets.UTF_8;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.LogManager;

public class Rainmaker {
    /* Injection info */
    public static int injectionCNT    = 0;
    public static String injectCallSiteStr;
    public static String clientReqID  = "XXX";
    public static ReentrantLock lock  = new ReentrantLock();
    public static final int sleepTime = 102;
    private static int seqToInject     = 0;
    private static Map<String, List<String>> injectTestCallSitesMap;

    /* MockServer client */
    private static ClientAndServer mockServer;
    private static ClientAndServer blockRequestServer;

    /* Retrieve HTTP traffic vars */
    JSONArray recordedRequests;
    private static final int noTraffic = -1;
    private static final int exceptionHappenedWhenRetrieving = -3;
    private static List<String> skippedTestCaseExceptionHappens;
    private static int resultNameSpecializedEnum             = 2;
    private static boolean exemptFromRetrieving              = false;

    /* Test results */
    private static int testSuccess = 0, testFail = 0, testSkipped = 0;

    /* Testing time */
    Duration timeElapsed;
    Duration eachRoundTimeElapsed;
    private static Map<String, String> testRoundTimeMap;
    public static final SimpleDateFormat runTimestampFormat = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss");

    /* Configuration vars */
    public static String projPath;
    public static String projPathRoot;
    public static String projName;
    public static String testDLL;
    public static String rainmakerPath;
    public static String torchPath;
    public static String rainmakerPolicy;
    public static String resultDir;
    public static String statDir;
    public static String projectName;
    public static int cosmosErrorCode;
    public static boolean appFlag;
    public static String cloudService;

    private static String vanillaDir;
    private static boolean vanillaRun = false;
    private final boolean testFlag;
    private final boolean includePUTTestFlag;
    private final boolean fullTestFlag;
    private final boolean validationFlag;
    private final boolean cosmosAppFlag;
    private String configCallSiteStr;

    /* Validation flags */
    private final int validationRound;
    private final boolean fullValidationFlag;
    private final List<String> partialTestOrValidationNameList;

    /* Output directory */
    public static String curTestStatDirWithSeq;
    public static String curTestOutcomeDir;

    /**
     * Rainmaker configuration construction.
      * @param config configuration for Rainmaker testing.
     */
    public Rainmaker(JSONObject config) {
        projPath            = System.getProperty("user.home")+"\\"+config.getString("project_test_path");
        projPathRoot        = config.getString("project_path_root");

        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(runTimestampFormat.format(timestamp));

        testDLL         = config.getString("test_dll");
        rainmakerPolicy = config.getString("policy");
        vanillaRun      = Objects.equals(rainmakerPolicy, "vanilla");
        projectName     = config.getString("project").toLowerCase();

        rainmakerPath = System.getProperty("user.home")+"\\"+config.getString("rainmaker_path");
        torchPath     = System.getProperty("user.home")+"\\"+config.getString("torch_path");
        resultDir     = Paths.get(System.getProperty("user.dir"), "..\\..\\results", config.getString("project").toLowerCase()).toString();
        if (!vanillaRun)
           vanillaDir = Paths.get(System.getProperty("user.dir"), "..\\..\\results", config.getString("stat_dir").split("\\\\")[1]).toString();
        statDir = Paths.get(System.getProperty("user.dir"), config.getString("stat_dir")).toString();

        if (config.has("service"))
            cloudService = config.getString("service");
        else
            cloudService = "Azure Storage";

        if (config.has("test"))
            testFlag = config.getBoolean("test");
        else
            testFlag = true;
        
        if (config.has("include_PUT_test"))
            includePUTTestFlag = config.getBoolean("include_PUT_test");
        else
            includePUTTestFlag = false;

        if (config.has("full_test_or_vanilla"))
            fullTestFlag = config.getBoolean("full_test_or_vanilla");
        else
            fullTestFlag = true;

        if (config.has("validation"))
            validationFlag = config.getBoolean("validation");
        else
            validationFlag = false;

        if (config.has("full_validation"))
            fullValidationFlag = config.getBoolean("full_validation");
        else
            fullValidationFlag = false;

        if (config.has("app_flag")) {
            appFlag = config.getBoolean("app_flag");
            if (config.has("config_callsite"))
                configCallSiteStr = config.getString("config_callsite");
            else 
                configCallSiteStr = "NO_CONFIG_CALLSITE";
        }
        else
            appFlag = false;

        if (config.has("cosmos_app")) {
            cosmosAppFlag = config.getBoolean("cosmos_app");
            appFlag = cosmosAppFlag;
            if (config.has("config_callsite"))
                configCallSiteStr = config.getString("config_callsite");
            else 
                configCallSiteStr = "NO_CONFIG_CALLSITE";
        }
        else
            cosmosAppFlag = false;

        if (config.has("validation") && config.has("validation_round"))
            validationRound = config.getInt("validation_round");
        else
            validationRound = 1;

        if (config.has("cosmos_error_code") && cosmosAppFlag)
            cosmosErrorCode = config.getInt("cosmos_error_code");
        else
            cosmosErrorCode = 503;

        if (vanillaRun)
            projName = config.getString("project") + "_" + runTimestampFormat.format(timestamp);
        else if (validationFlag && !testFlag)
            projName = config.getString("project") + "-validation-round_" + runTimestampFormat.format(timestamp);
        else if (testFlag && !validationFlag)
            projName = config.getString("project") + "-injection-round_" + runTimestampFormat.format(timestamp);
        else if (testFlag) {
            System.out.println("full_test_or_vanilla and full_validation cannot be true at the same time");
            System.exit(0);
        }
        else {
            System.out.println("Should specify whether it is a test or validation run when it is not vanilla!");
            System.exit(0);
        }
        System.out.println(projName);

        if (testFlag && config.has("partial_test")) {
            JSONArray jsonArray = config.getJSONArray("partial_test");
            partialTestOrValidationNameList = new ArrayList<String>();
            for (int i=0; i<jsonArray.length(); i++){
                // Adding each element of JSON array into ArrayList
                partialTestOrValidationNameList.add(jsonArray.getString(i));
            }
        }
        else if (validationFlag && config.has("partial_validation")) {
            JSONArray jsonArray = config.getJSONArray("partial_validation");
            partialTestOrValidationNameList = new ArrayList<String>();
            for (int i=0; i<jsonArray.length(); i++){
                // Adding each element of JSON array into ArrayList
                partialTestOrValidationNameList.add(jsonArray.getString(i));
            }
        }
        else {
            JSONArray jsonArray = config.getJSONArray("partial_test");
            partialTestOrValidationNameList = new ArrayList<String>();
            for (int i=0; i<jsonArray.length(); i++){
                // Adding each element of JSON array into ArrayList
                partialTestOrValidationNameList.add(jsonArray.getString(i));
            }
        }

        File statFile = new File("stat/"+projName);
        if(statFile.mkdir()){
            System.out.println("stat folder is created successfully");
        }
        else {
            System.out.println("Error Found!");
        }

        File outcomeFile = new File("outcome/"+projName);
        if (outcomeFile.mkdir()){
            System.out.println("outcome folder is created successfully");
        }
        else {
            System.out.println("Error Found!");
        }
        //  System.exit(0);
    }

    /**
     * Find the test cases at the beginning of the reference round.
     * @return A list of tests found by dotnet test.
     * @throws Exception
     */
    private static List<String> findTestCases() throws Exception {
        List<String> listTestCaseNames = new ArrayList<String>();
        skippedTestCaseExceptionHappens = new ArrayList<String>();
        File dirTest = new File(projPath);
        try {
            // System.out.println(projPath + "\\" + "test.runsettings");
            ProcessBuilder processBuilder;
            // Some projects may need vstest.console.exe
            // processBuilder = new ProcessBuilder("cmd.exe", "/c",
            //      "\"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\CommonExtensions\\Microsoft\\TestWindow\\vstest.console.exe\" "
            //                        + "/lt "+ testDLL);
            processBuilder = new ProcessBuilder("cmd.exe", "/c", "dotnet test " + testDLL + " --list-tests");
            processBuilder.directory(dirTest);
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            InputStreamReader isr = new InputStreamReader(process.getInputStream());
            BufferedReader rdr = new BufferedReader(isr);
            String line;
            boolean testNamesStartFlag = false;
            boolean testNamesEndFlag = false;
            int testRunForCNT = 0;
            while ((line = rdr.readLine()) != null) {
                System.out.println(line);
                // TODO: if it is using NUnit test framework, then it does not have this key sentence
                if (line.contains("Test run for")) {
                    testRunForCNT += 1;
                    if (testRunForCNT == 2) {
                        testNamesEndFlag = true;
                    }
                }
                if (testNamesStartFlag && !testNamesEndFlag) {
                    listTestCaseNames.add(line.trim().replace(":", "."));
                }
                if (line.contains("The following Tests are available:")) {
                    testNamesStartFlag = true;
                }
            }
            process.waitFor();
        } catch (Exception e){
            e.printStackTrace();
        }
        return listTestCaseNames;
    }

    /**
     * Construct the test case that needs to be injected (Passed in the data collection round).
     * The key is the test case name => list of unique call sites.
     * @param testRun
     * @return
     */
    public static Map<String, List<String>> constructRequestNumMapping(boolean testRun) {
        Map<String, List<String>> testCallSitesMap = new HashMap<String, List<String>>();
        if (testRun) {
            // Test run
            // TODO: maybe should not rely on this PASSED_test.csv
            Path passedFilePath = Paths.get(vanillaDir, "PASSED_test.csv");
            try (BufferedReader csvBufferReader = new BufferedReader(new FileReader(passedFilePath.toString()))) {
                String testName;
                while ((testName = csvBufferReader.readLine()) != null) {
                    Path callSiteFilePath = Paths.get(statDir, testName, "0", "CALLSITE.csv");
                    try (BufferedReader callSiteReader = new BufferedReader(new FileReader(callSiteFilePath.toString()))) {
                        String line;
                        List<String> callSitesInSingleTestList = new ArrayList<>();
                        while ((line = callSiteReader.readLine()) != null) {
                            String[] values = line.split("\t");
                            if (values[0].isEmpty())
                                continue;
                            if (values[0].equals("[', , ,']"))
                                continue;
                            String callSiteString = Objects.requireNonNull(Optional.of(values[0].trim())
                                    .filter(str -> str.length() != 0)
                                    .map(str -> str.substring(2, str.length() - 2))
                                    .orElse(values[0].trim())).replace("\\\\", "\\").trim();
                            callSitesInSingleTestList.add(callSiteString);
                        }
                        testCallSitesMap.put(testName, callSitesInSingleTestList);
//                        System.out.println(testName);
                    } catch (FileNotFoundException fe) {
                        continue;
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        else {
            // Validation run
            Path bugInspectionPath = Paths.get(resultDir, "bug_inspection.csv");
            System.out.println(resultDir);
            try (BufferedReader csvBufferReader = new BufferedReader(new FileReader(bugInspectionPath.toString()))) {
                String testName;
                String callsiteToInject;
                String row;
                // Skip the header
                csvBufferReader.readLine();
                while ((row = csvBufferReader.readLine()) != null) {
                    System.out.println(row);
                    String[] values = row.split("\t");
                    
                    testName = values[0];
                    System.out.println(testName);
                    callsiteToInject = values[3];
                    // TODO: this may have a problem when we want to reproduce the injection for some tests - shld mod
                    if (Objects.equals(callsiteToInject, "Cannot find SDK API")) {
                        continue;
                    }
                    if (testCallSitesMap.containsKey(testName)) {
                        List<String> updateList = testCallSitesMap.get(testName);
                        updateList.add(callsiteToInject);
                        testCallSitesMap.put(testName, updateList);
                    }
                    else {
                        List<String> callSitesInSingleTestList = new ArrayList<>();
                        callSitesInSingleTestList.add(callsiteToInject.trim());
                        testCallSitesMap.put(testName, callSitesInSingleTestList);
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return testCallSitesMap;
    }

    /**
     * Start Rainmaker proxies.
     * @throws IOException
     */
    public void startRainmakerProxy() throws IOException {
        // Configure the socket timeout, otherwise when retrieving records, it may reach timeout
        ConfigurationProperties.maxSocketTimeout(120000);
        mockServer = ClientAndServer.startClientAndServer(10000, 10001, 10002, 18081);
        System.out.println("Mockserver is running: " + mockServer.isRunning());

        if (Objects.equals(rainmakerPolicy, "request_block")) {
            blockRequestServer = ClientAndServer.startClientAndServer(30000);
            System.out.println("BlockRequestServer is running: " + blockRequestServer.isRunning());
        }

        if (Objects.equals(rainmakerPolicy, "timeout_first_request_block")) {
            blockRequestServer = ClientAndServer.startClientAndServer(30000);
            System.out.println("BlockRequestServer is running: " + blockRequestServer.isRunning());
        }

        ConfigurationProperties.logLevel("INFO");
        String loggingConfiguration = "" +
                "java.util.logging.FileHandler.pattern = mockserver.log\n" +
                "java.util.logging.FileHandler.formatter = java.util.logging.SimpleFormatter\n" +
                "java.util.logging.FileHandler.limit=50000\n" +
                "java.util.logging.FileHandler.count=5\n" +
                "java.util.logging.FileHandler.level = INFO\n";
        LogManager.getLogManager().readConfiguration(new ByteArrayInputStream(loggingConfiguration.getBytes(UTF_8)));
    }

    /**
     * Stop Rainmaker proxies.
     */
    public void stopRainmakerProxy() {
        mockServer.stop();
        if (Objects.equals(rainmakerPolicy, "request_block")) {
            blockRequestServer.stop();
        }
        else if (Objects.equals(rainmakerPolicy, "timeout_first_request_block")) {
            blockRequestServer.stop();
        }
    }

    /**
     * Set the Mockserver request expectation according to the Rainmaker configuration.
     */
    private void setForwardExpectation() {
        if (Objects.equals(rainmakerPolicy, "vanilla"))
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(InjectionPolicy.RequestForwardAndResponseCallback.class)
                    );
        else if (Objects.equals(rainmakerPolicy, "timeout_success"))
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(TimeoutSuccess.RequestForwardAndResponseCallback.class)
                    );
        else if (Objects.equals(rainmakerPolicy, "timeout_4s"))
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(Timeout.RequestForwardAndResponseCallback.class)
                    );
        else if (Objects.equals(rainmakerPolicy, "timeout_blind")) {
            if (cosmosAppFlag)
                mockServer.when(
                                request()
                        )
                        .forward(
                                callback().withCallbackClass(TimeoutBlindCosmos.RequestForwardAndResponseCallback.class)
                        );
            else
                mockServer.when(
                                request()
                        )
                        .forward(
                                callback().withCallbackClass(TimeoutBlind.RequestForwardAndResponseCallback.class)
                        );
        }
        else if (Objects.equals(rainmakerPolicy, "timeout_blind_all"))
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(TimeoutAll.RequestForwardAndResponseCallback.class)
                    );
        else if (Objects.equals(rainmakerPolicy, "request_block")) {
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(RequestBlockPolicy.RequestForwardAndResponseCallback.class)
                    );
            blockRequestServer.when(
                            request()
                    )
                    .respond(
                            callback().withCallbackClass(RequestBlockMockserver.RequestBlockExpectationResponseCallback.class)
                    );
        }
        else if (Objects.equals(rainmakerPolicy, "timeout_first_request_block")) {
            mockServer.when(
                            request()
                    )
                    .forward(
                            callback().withCallbackClass(TimeoutFirstRequestBlock.RequestForwardAndResponseCallback.class)
                    );
            blockRequestServer.when(
                            request()
                    )
                    .respond(
                            callback().withCallbackClass(RequestBlockMockserver.RequestBlockExpectationResponseCallback.class)
                    );
        }
    }

    /**
     * Reset the Rainmaker proxy after each test run.
     */
    private void resetMockserver() {
        mockServer.reset();
        if (Objects.equals(rainmakerPolicy, "request_block")) {
            blockRequestServer.reset();
        }
        else if (Objects.equals(rainmakerPolicy, "timeout_first_request_block")) {
            blockRequestServer.reset();
        }
    }

    /**
     * Check which cloud service the current test had used.
     * @return 1 if there are requests and responses.
     * return -1 if there is no traffic.
     */
    private int retrieveRequestsAndResponses() {
        System.out.println("Going to retrieve requests and responses..");
        try {
            recordedRequests = new JSONArray(mockServer.retrieveRecordedRequestsAndResponses(request(), Format.JSON));
        } catch (Exception e) {
            e.printStackTrace();
            return exceptionHappenedWhenRetrieving;
        }

        if (recordedRequests.length() == 0) {
            System.out.println("No requests and responses found.");
            return noTraffic;
        }
        else
            return 1;
    }

    /**
     * Handle CosmosDB application.
     */
    private void handleCosmosApp() {
        setForwardExpectation();
        long start = System.currentTimeMillis();
        while (true) {
            long finish = System.currentTimeMillis();
            long timeElapsed = finish - start;
            if (timeElapsed > 180000) {
                retrieveRequestsAndResponses();
                curTestStatDirWithSeq = "stat/" + projName + "/" + "cosmosAppWork" + "/" + seqToInject;
                new File(curTestStatDirWithSeq).mkdirs();
                retrieveHTTPTrafficInAllServers();
                break;
            }
        }
    }

    /**
     * Start the test round for the application under test.
     * @throws Exception
     */
    public void rainmakerTest() throws Exception {
        List<String> listTestNames = new ArrayList<String>();
        if (!appFlag) {
            if (vanillaRun) {
                if (fullTestFlag) {
                    listTestNames = findTestCases();
                    System.out.println("Collected test cases' names:" + listTestNames);
                    System.out.println("Collected test cases list size:" + listTestNames.size());
                    // Debug
                    // System.exit(0);
                }
                else {
                    if (partialTestOrValidationNameList.size() == 0) {
                        System.out.println("When doing test data collection partially, should specify some test case name(s) in the config.json file!");
                        System.exit(0);
                    }
                    else {
                        listTestNames = partialTestOrValidationNameList;
                        System.out.println("Going to run partial test cases:" + listTestNames);
                    }
                }
            }
            else {
                // Fault injection test round
                if (testFlag) {
                    injectTestCallSitesMap = constructRequestNumMapping(true);
                    // System.out.println(injectTestCallSitesMap.toString());
                    if (fullTestFlag) {
                        List<String> testNamesWithNumList = new ArrayList<String>(injectTestCallSitesMap.keySet());
                        System.out.println("Going to inject test cases:" + testNamesWithNumList);
                        System.out.println("Going to inject test cases list size:" + testNamesWithNumList.size());
                        // Sort the test names based on the number of unique call site.
                        // Put the test with the fewer number of call sites at the front.
                        testNamesWithNumList.sort(new Comparator<String>() {
                            public int compare(String left, String right) {
                                return Integer.compare(injectTestCallSitesMap.get(left).size(), injectTestCallSitesMap.get(right).size());
                            }
                        });
                        listTestNames = testNamesWithNumList;
                    }
                    else {
                        if (partialTestOrValidationNameList.size() == 0) {
                            System.out.println("When doing fault injection partially, should specify some test case name(s) in the config.json file!");
                            System.exit(0);
                        }
                        else {
                            listTestNames = partialTestOrValidationNameList;
                            System.out.println("Going to inject faults to partial test cases:" + listTestNames);
                        }
                    }
                }
                // Failure reproduction round
                if (validationFlag) {
                    injectTestCallSitesMap = constructRequestNumMapping(false);
                    // System.out.println(injectTestCallSitesMap.toString());
                    if (fullValidationFlag) {
                        List<String> testNamesWithNumList = new ArrayList<String>(injectTestCallSitesMap.keySet());
                        System.out.println("Going to validate test cases' names:" + testNamesWithNumList);
                        System.out.println("Going to validate test cases list size:" + testNamesWithNumList.size());
                        System.out.println("injectTestCallSitesMap:" + injectTestCallSitesMap.toString());
                        // Sort the test names based on the number of unique call site.
                        // Put the test with the fewer number of call sites at the front.
                        testNamesWithNumList.sort(new Comparator<String>() {
                            public int compare(String left, String right) {
                                return Integer.compare(injectTestCallSitesMap.get(left).size(), injectTestCallSitesMap.get(right).size());
                            }
                        });
                        listTestNames = testNamesWithNumList;
                    }
                    else {
                        if (partialTestOrValidationNameList.size() == 0) {
                            System.out.println("When doing validation partially, should specify some test case name(s) in the config.json file!");
                            System.exit(0);
                        }
                        else {
                            listTestNames = partialTestOrValidationNameList;
                            System.out.println("Going to validate partial test failures:" + listTestNames);
                        }
                    }
                }
            }
        }
        else {
            // If the software under test is an application.
            listTestNames = new ArrayList<String>();
            listTestNames.add("AppTesting");
        }

        if (cosmosAppFlag) {
            handleCosmosApp();
            return;
        }

        try {
            File dirTest = new File(rainmakerPath);
            System.out.println("*****************************************");
            skippedTestCaseExceptionHappens = new ArrayList<String>();
            testRoundTimeMap = new HashMap<String, String>();

            Instant startTime = Instant.now();
            // File writer to write requests with missing x-Location header to a file
            FileWriter fwReqWithMissingHeader = new FileWriter("request-missing-header.txt");

//            System.out.println("injectTestCallSitesMap = " + injectTestCallSitesMap.toString());
//            System.out.println("injectTestCallSitesMap size = " + injectTestCallSitesMap.size());
            for (String curTestCaseName: listTestNames) {
                /* ********************************************** */
                // Skip stream limit tests in Orleans.
                if (curTestCaseName.contains("StreamLimitTests"))
                    continue;
                System.out.println(curTestCaseName);
                /* ********************************************** */
                // if (curTestCaseName.contains("AzureEmulatedBlobStorageTest") && projectName.equals("storage"))
                //     continue;

                // if (!curTestCaseName.contains("Aws") && projectName.equals("storage"))
                //     continue;

                // if (curTestCaseName.contains("Aws") && projectName.equals("storage"))
                //     continue;
                /* ********************************************** */

                // dotnet test cannot run single test with parenthesis in the test name.
                if (curTestCaseName.contains("(")) {
                    if (!includePUTTestFlag)
                        continue;
                    else {
                        if (projectName.contains("fhir")) {
                            int count = StringUtils.countMatches(curTestCaseName, "(");
                            System.out.println("number of open brackets: "+count);
                            if (count == 1) {
                                curTestCaseName = curTestCaseName.split("\\).")[1];
                            }
                            else if (count == 2) {
                                // Two brackets occurrence
                                curTestCaseName = StringUtils.substringBetween(curTestCaseName, ").", "(");
                                System.out.println("curTestCaseName:");
                                System.out.println(curTestCaseName);
                                // fhir tests are so time-consuming, so ignore the PUT which has param except Cosmos config
                                continue;
                            }
                            else
                                curTestCaseName = curTestCaseName.split("\\(")[0];

                            if (curTestCaseName.length() <= 5) 
                                continue;
                        }
                        else {
                            curTestCaseName = curTestCaseName.split("\\(")[0];
                        }
                    }
                }

                String curTestStatDir = "stat/"+projName+"/"+curTestCaseName;
                curTestOutcomeDir     = "outcome/"+projName+"/"+curTestCaseName;
                new File(curTestStatDir).mkdirs();
                new File(curTestOutcomeDir).mkdirs();

                int totalInjectNum;
                if (vanillaRun)
                    totalInjectNum = 1;
                else if (projName.contains("AWSTest"))
                    // This is for the AWS toy application made by us.
                    totalInjectNum = 10;
                else
                    totalInjectNum = injectTestCallSitesMap.get(curTestCaseName).size() * validationRound;

                // System.out.println(injectTestCallSitesMap.get(curTestCaseName));
                System.out.println("Total injection rounds would be: "+totalInjectNum);
                for (int seq=0; seq < totalInjectNum; seq++) {
                    seqToInject = seq / validationRound;

                    if (vanillaRun)
                        injectCallSiteStr = "VANILLA_RUN_NO_INJECTION_STRING";
                    else if (appFlag)
                        injectCallSiteStr = configCallSiteStr;
                    else
                        injectCallSiteStr = injectTestCallSitesMap.get(curTestCaseName).get(seqToInject);

                    if (appFlag) 
                        curTestStatDirWithSeq = "stat/"+projName+"/"+"AppTesting"+"/"+seqToInject;
                    else
                        curTestStatDirWithSeq = "stat/"+projName+"/"+curTestCaseName+"/"+seqToInject;
                    
                    new File(curTestStatDirWithSeq).mkdirs();

                    System.out.println("Setting forwarding expectations for an incoming test..");
                    Instant eachRoundStartTime = Instant.now();
                    setForwardExpectation();
                    System.out.println("=========================================");
                    System.out.println("Current test case: " + curTestCaseName);

                    ProcessBuilder processBuilder;
                    if (appFlag) {
                        // Application testing.
                        processBuilder = new ProcessBuilder("cmd.exe", "/c",
                           "dotnet run --project " + testDLL);
                    }
                    else if (!includePUTTestFlag) {
                        // If we do not consider PUT test, the fully qualified name of the test can be used.
                        processBuilder = new ProcessBuilder("cmd.exe", "/c",
                                "dotnet test "+ testDLL + " --blame-hang-timeout 10m --logger trx --filter FullyQualifiedName=" + curTestCaseName);
                    }
                    else {
                        processBuilder = new ProcessBuilder("cmd.exe", "/c",
                                "dotnet test "+ testDLL + " --blame-hang-timeout 10m --logger trx --filter " + curTestCaseName);
                    }

                    processBuilder.directory(dirTest);
                    processBuilder.redirectErrorStream(true);
                    Process process = processBuilder.start();

                    BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String line;
                    while ((line = in.readLine()) != null) {
                        System.out.println(line);
                        if (line.contains("Failed:     1")) {
                            resultNameSpecializedEnum = 0;
                            testFail += 1;
                        } else if (line.contains("Skipped:     1")) {
                            resultNameSpecializedEnum = 1;
                            testSkipped += 1;
                        } else if (line.contains("Passed:     1")) {
                            resultNameSpecializedEnum = 2;
                            testSuccess += 1;
                        }
                    }

                    process.waitFor();
                    injectionCNT = 0;

                    File folder = new File(rainmakerPath + "/TestResults");
                    File[] listOfFiles = folder.listFiles();

                    assert listOfFiles != null;
                    if (listOfFiles.length == 0) {
                        System.out.println("Test result folder should not be empty.. going to exit");
                        System.exit(0);
                    }
                    else {
                        int fCNT = 0;
                        for (File listOfFile : listOfFiles) {
                            if (listOfFile.isFile()) {
                                // System.out.println("File " + listOfFile.getName());
                                String resultString;
                                if (resultNameSpecializedEnum == 0) {
                                    resultString = "outcome/" + projName + "/" + curTestCaseName + "/0-failed-test-result-"
                                            + seq + "-" + fCNT + ".trx";
                                }
                                else if (resultNameSpecializedEnum == 1) {
                                    resultString = "outcome/" + projName + "/" + curTestCaseName + "/1-skipped-test-result-"
                                            + seq + "-" + fCNT + ".trx";
                                }
                                else {
                                    resultString = "outcome/" + projName + "/" + curTestCaseName + "/test-result-"
                                            + seq + "-" + fCNT + ".trx";
                                }
                                Files.deleteIfExists(Paths.get(resultString));
                                listOfFile.renameTo(new File(resultString));
                            }
                            else if (listOfFile.isDirectory()) {
                                // System.out.println("Directory: " + listOfFile.getName());
                                continue;
                            }
                            fCNT++;
                        }
                    }

                    int retrieveTrafficResult;
                    // Waiting for all the pending injection callback to finish before retrieving all the requests
                    boolean isLockAcquired = lock.tryLock(2*sleepTime, TimeUnit.SECONDS);
                    if (isLockAcquired) {
                        try {
                            retrieveTrafficResult = retrieveRequestsAndResponses();
                        }
                        finally {
                            lock.unlock();
                        }
                    }
                    else {
                        retrieveTrafficResult = exceptionHappenedWhenRetrieving;
                        System.out.println("Unable to acquire the lock when preparing to retrieve requests and responses.");
                        System.exit(0);
                    }

                    System.out.println("=========================================");
                    if (!exemptFromRetrieving && retrieveTrafficResult != exceptionHappenedWhenRetrieving) {
                        //testSuccess += 1;
                        retrieveHTTPTrafficInAllServers();
                    } else if (!exemptFromRetrieving) {
                        testSuccess -= 1;
                        skippedTestCaseExceptionHappens.add(curTestCaseName);
                        System.out.println("Skip test " + curTestCaseName + " due to exception when retrieving!");
                    }
                    Instant eachRoundEndTime = Instant.now();
                    eachRoundTimeElapsed = Duration.between(eachRoundStartTime, eachRoundEndTime);
                    testRoundTimeMap.put(curTestCaseName, humanReadableFormat(eachRoundTimeElapsed));
                    exemptFromRetrieving = false;
                    System.out.println("Resetting all expectations for the finished test (clear all the expectations and logs)... test name:" + curTestCaseName);
                    resetMockserver();

                    singleTestStat(curTestCaseName);
                    if (curTestCaseName.contains("AwsSQSTest") && projectName.equals("storage")) {
                        // For SQS service, it needs 60 seconds to be achieve consistency.
                        System.out.println("********Sleep 61 seconds when it is a AWS SQS test (consistency model)********");
                        TimeUnit.SECONDS.sleep(61);
                    }
                }
            }

            Instant finishTime = Instant.now();
            timeElapsed = Duration.between(startTime, finishTime);
            fwReqWithMissingHeader.close();

            System.out.println("*****************************************");
            statsOfRESTAPIs();
            // System.out.println("The total number of requests is: " + totalRequestNum);
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    /**
     * Collect al the requests during the test round.
     */
    public void retrieveHTTPTrafficInAllServers() {
        System.out.println("Retrieving all the HTTP traffic..");
        CollectHTTPTraffic trafficCollector = new CollectHTTPTraffic(recordedRequests);
        trafficCollector.truncateRequestBody();
        trafficCollector.saveHTTPTraffic();
    }

    /**
     * Convert the time span to human-readable format.
     * @param duration
     * @return
     */
    public static String humanReadableFormat(Duration duration) {
        return duration.toString()
                .substring(2)
                .replaceAll("(\\d[HMS])(?!$)", "$1 ")
                .toLowerCase();
    }

    /**
     * Statistics for a single test - output to the overview file.
     * @param curTestCaseName current test case name.
     * @throws IOException
     */
    public void singleTestStat(String curTestCaseName) throws IOException {
        FileWriter fwTestStat = new FileWriter(curTestStatDirWithSeq+"/overview.txt");
        fwTestStat.write("Running time for this test: " + testRoundTimeMap.get(curTestCaseName) + "\n");
        fwTestStat.close();
    }

    /**
     * On-the-fly statistics for the REST API usage.
     * This statistics may not be accurate.
     * @throws IOException
     */
    public void statsOfRESTAPIs() throws IOException {
        FileWriter fwTestTime = new FileWriter("test-running-time-stats.txt");
        for (Map.Entry<String,String> entry : testRoundTimeMap.entrySet())
            fwTestTime.write(entry.getKey() + "\t" + entry.getValue() + "\n");
        fwTestTime.close();

        FileWriter fwExcp = new FileWriter("skipped-tests.txt");
        for (String entry : skippedTestCaseExceptionHappens)
            fwExcp.write(entry + "\n");
        fwExcp.close();

        FileWriter fw = new FileWriter("test-stats.txt");
        fw.write("Total Running Time: " + humanReadableFormat(timeElapsed));
        fw.close();

        System.out.println("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%");
        System.out.println("Total Running Time: " + humanReadableFormat(timeElapsed));
        System.out.println("total number of Failed tests: " + testFail);
        System.out.println("total number of Succeeded tests: " + testSuccess);
        System.out.println("total number of Skipped tests: " + testSkipped);
    }

    //    public void rainmakerAppTest() throws Exception {
    //        setForwardExpectation()
    //        long start = System.currentTimeMillis();
    //        while (true) {
    //            long finish = System.currentTimeMillis();
    //            long timeElapsed = finish - start;
    //            if (timeElapsed > 30000) {
    //                checkWhichServiceUsed();
    //                curTestStatDirWithSeq = "stat/"+projName+"/"+"XXXX"+"/"+seqToInject;
    //                new File(curTestStatDirWithSeq).mkdirs();
    //                retrieveHTTPTrafficInAllServers("XXX", 0);
    //                break;
    //            }
    //        }
    //    }
}

