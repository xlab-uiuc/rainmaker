@echo off
set ROOT=%CD%

rem Use the following to attach a debugger
setx TORCH_DYNAMIC_MessageboxAtAttach 0 /m

setx COR_PROFILER {cf0d821e-299b-5307-a3d8-b283c03916dd} /m
setx COR_ENABLE_PROFILING 1 /m
setx COR_PROFILER_PATH_32 "%ROOT%\microsoft.Torch.Dynamic.Engine_Win32.dll" /m
setx COR_PROFILER_PATH_64 "%ROOT%\microsoft.Torch.Dynamic.Engine_64.dll" /m
setx COMPLUS_ProfAPI_ProfilerCompatibilitySetting EnableV2Profiler /m
setx TORCH_CALLBACK_HOME "%ROOT%\Engine" /m

setx CORECLR_PROFILER {cf0d821e-299b-5307-a3d8-b283c03916dd} /m
setx CORECLR_ENABLE_PROFILING 1 /m
setx CORECLR_PROFILER_PATH_32 "%ROOT%\microsoft.Torch.Dynamic.Engine_Win32.dll" /m
setx CORECLR_PROFILER_PATH_64 "%ROOT%\microsoft.Torch.Dynamic.Engine_x64.dll" /m
setx COMPLUS_ProfAPI_ProfilerCompatibilitySetting EnableV2Profiler /m
setx TORCHCORE_CALLBACK_HOME "%ROOT%\Engine" /m


echo Profiler is On for %BIT% bits. Profiler paths are below:
echo Framework: %COR_PROFILER_PATH%
echo NetCore: %CORECLR_PROFILER_PATH%