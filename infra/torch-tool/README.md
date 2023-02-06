# User guide:
## Usage
This folder contains a tool to inject faults into managed application, based on .NET profiling APIs.

1. Enabling fault injection
	- From current folder, run `ProfOn.cmd`, or `ProfOn.ps1`, or `ProfOnX.cmd` (for setting machine level env variable of Rainmaker)
	
	`torch.ps1` will generate a new PowerShell doing all instrumentation there. Example for `torch.ps1`: `Engine\torch.ps1 "dotnet test --filter FullyQualifiedName=Tester.AzureUtils.AzureQueueDataManagerTests.AQ_Standalone_1 --no-build --no-restore"`
	
2. Inject faults:
	- Just run your target application from the shell where you ran `ProfOn.cmd`.
	
	Note: `ProfOn.cmd` sets environment variable for the current process (the shell) 
		and its child processeses (target app run from the shell). You may consider
		setting the environment variables for a speciifc user or the entire machine. 
	
	Note: if you have enabled profiler with `ProfOn.ps1` or `ProfOnX.cmd`, profiling is enabled for the entire machine and you can run the application from any other shell
	- Customizing faults:
		- Edit the TorchConfig.json file. It contains a collection of fault rules. Each rule contains three components: 
		
		`target`: a wildcard pattern of a target function we want to inject fault into
		
		`when`: when should the fault be injected. Currently available options are: "Never", "Always", "OnKthTime(2)", "OnEveryKthTime(3)", "WithProbability(0.5)"
		`fault`: name and parameter of the fault
3. Disable fault injection: `ProfOff.cmd` or `ProfOff.ps1` or `ProfOffX.cmd` (`Torch.ps1` will be closed automatically)

## Usage tips:
Use this shortcut to turn off and turn again: ```.\ProfOff.ps1; cd ..; .\CopyAll.cmd; cd Engine; .\ProfOn.ps1```

## Debug the tool
1. Change the value  “TORCH_DYNAMIC_MessageboxAtAttach” in Torch.ps1 from 0 to 1
2. Run the target test case
3. Run Visual Studio as admin 
4. Click 'Debug', and then 'Attach to Process'
5. Sort the process based on its names (since there are so many running processes), select the process with tittle: "Torch"

Event Viewer will also help.

## Errors
We encounter NuGet.targets error :

``NuGet.targets(130, 5): error : Could not load file or assembly 'Microsoft.Torch.Dynamic.CallbackCore, Version=1.0.0.0...'``

Solution for this: 
  1. Open Developer Command Prompt for VS 2019 with admin permission
  2. ``gacutil /i Microsoft.Torch.Dynamic.CallbacksCore.dll``
  3. ``gacutil /i Microsoft.Torch.Dynamic.Callbacks.dll``

To un-insert these two dll from the cache, run:
  1. ``gacutil /u Microsoft.Torch.Dynamic.CallbacksCore`` (without .dll)
  2. ``gacutil /u Microsoft.Torch.Dynamic.Callbacks``
