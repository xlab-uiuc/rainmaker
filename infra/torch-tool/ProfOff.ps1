[System.Environment]::SetEnvironmentVariable("COR_ENABLE_PROFILING", "0", "Machine");
[System.Environment]::SetEnvironmentVariable("CORECLR_ENABLE_PROFILING", "0", "Machine");

[System.Environment]::SetEnvironmentVariable("COMPLUS_ProfAPI_ProfilerCompatibilitySetting", $null, "Machine");

[System.Environment]::SetEnvironmentVariable("COR_PROFILER", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("COR_PROFILER_PATH_32", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("COR_PROFILER_PATH_64", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("COMPLUS_ProfAPI_ProfilerCompatibilitySetting", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("TORCH_CALLBACK_HOME", $null, "Machine");

[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER_PATH_32", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("CORECLR_PROFILER_PATH_64", $null, "Machine");
[System.Environment]::SetEnvironmentVariable("TORCHCORE_CALLBACK_HOME", $null, "Machine");

[System.Environment]::SetEnvironmentVariable("TORCH_DYNAMIC_MessageboxAtAttach",$null, "Machine");

echo "Profiler is Off"