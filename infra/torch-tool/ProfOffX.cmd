@echo off
REM SET mvar="HKCU\Environment"
SET mvar="HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

reg delete %mvar% /v TORCH_DYNAMIC_MessageboxAtAttach /f

reg delete %mvar% /v COMPLUS_ProfAPI_ProfilerCompatibilitySetting /f

reg delete %mvar% /v COR_PROFILER /f
reg delete %mvar% /v COR_ENABLE_PROFILING /f
reg delete %mvar% /v COR_PROFILER_PATH_32 /f
reg delete %mvar% /v COR_PROFILER_PATH_64 /f
reg delete %mvar% /v TORCH_CALLBACK_HOME /f


reg delete %mvar% /v CORECLR_PROFILER /f
reg delete %mvar% /v CORECLR_ENABLE_PROFILING /f
reg delete %mvar% /v CORECLR_PROFILER_PATH_32 /f
reg delete %mvar% /v CORECLR_PROFILER_PATH_64 /f
reg delete %mvar% /v TORCHCORE_CALLBACK_HOME /f

echo Profiler is off


