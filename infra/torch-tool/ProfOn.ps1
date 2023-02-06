$RootDir=$PSScriptRoot

[System.Environment]::SetEnvironmentVariable("COR_ENABLE_PROFILING", "1", "Machine")
[System.Environment]::SetEnvironmentVariable("COR_PROFILER", "{cf0d821e-299b-5307-a3d8-b283c03916dd}", "Machine")
[System.Environment]::SetEnvironmentVariable("COR_PROFILER_PATH_32", $RootDir + "\Microsoft.Torch.Dynamic.Engine_Win32.dll", "Machine")
[System.Environment]::SetEnvironmentVariable("COR_PROFILER_PATH_64", $RootDir + "\Microsoft.Torch.Dynamic.Engine_x64.dll", "Machine")
[System.Environment]::SetEnvironmentVariable("COMPLUS_ProfAPI_ProfilerCompatibilitySetting", "EnableV2Profiler", "Machine")
[System.Environment]::SetEnvironmentVariable("TORCH_CALLBACK_HOME", $RootDir , "Machine")

[System.Environment]::SetEnvironmentVariable("CORECLR_ENABLE_PROFILING", "1", "Machine")
[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER", "{cf0d821e-299b-5307-a3d8-b283c03916dd}", "Machine")
[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER_PATH_32", $RootDir + "\Microsoft.Torch.Dynamic.Engine_Win32.dll", "Machine")
[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER_PATH_64", $RootDir + "\Microsoft.Torch.Dynamic.Engine_x64.dll", "Machine")
[System.Environment]::SetEnvironmentVariable("COMPLUS_ProfAPI_ProfilerCompatibilitySetting", "EnableV2Profiler", "Machine")
[System.Environment]::SetEnvironmentVariable("TORCHCORE_CALLBACK_HOME", $RootDir, "Machine")


[System.Environment]::SetEnvironmentVariable("TORCH_DYNAMIC_MessageboxAtAttach","0", "Machine")

Write-Host "Profiler is On for $BIT bits. Profiler paths are below:"
Write-Host "Framework: " 
[System.Environment]::GetEnvironmentVariable("COR_PROFILER_PATH_64", "Machine")
Write-Host "NetCore: "  
[System.Environment]::GetEnvironmentVariable("CORECLR_PROFILER_PATH_64", "Machine")