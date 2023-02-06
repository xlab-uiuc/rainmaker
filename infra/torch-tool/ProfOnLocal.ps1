$RootDir=$PSScriptRoot

$env:COR_ENABLE_PROFILING = 1
$env:COR_PROFILER = {cf0d821e-299b-5307-a3d8-b283c03916dd}
$env:COR_PROFILER_PATH_32 = $RootDir + "\Microsoft.Torch.Dynamic.Engine_Win32.dll"
$env:COR_PROFILER_PATH_64 = $RootDir + "\Microsoft.Torch.Dynamic.Engine_x64.dll"
$env:COMPLUS_ProfAPI_ProfilerCompatibilitySetting = "EnableV2Profiler"
$env:TORCH_CALLBACK_HOME = $RootDir

$env:CORECLR_ENABLE_PROFILING = 1
$env:CORECLR_PROFILER = {cf0d821e-299b-5307-a3d8-b283c03916dd}
$env:CORECLR_PROFILER_PATH_32 = $RootDir + "\Microsoft.Torch.Dynamic.Engine_Win32.dll"
$env:CORECLR_PROFILER_PATH_64 = $RootDir + "\Microsoft.Torch.Dynamic.Engine_x64.dll"
$env:COMPLUS_ProfAPI_ProfilerCompatibilitySetting = "EnableV2Profiler"
$env:TORCHCORE_CALLBACK_HOME = $RootDir

$env:TORCH_DYNAMIC_MessageboxAtAttach = 0

Write-Host "Profiler is On for $BIT bits. Profiler paths are below:"
Write-Host "Framework and NetCore: " 
Get-ChildItem Env:COR_PROFILER_PATH_32
Get-ChildItem Env:CORECLR_PROFILER_PATH_64