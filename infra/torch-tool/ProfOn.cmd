@echo off
set ROOT=%CD%

rem Use the following to attach a debugger
set TORCH_DYNAMIC_MessageboxAtAttach=0

set COR_PROFILER={cf0d821e-299b-5307-a3d8-b283c03916dd}
set COR_ENABLE_PROFILING=1
set COR_PROFILER_PATH_32=%ROOT%\Microsoft.Torch.Dynamic.Engine_Win32.dll
set COR_PROFILER_PATH_64=%ROOT%\Microsoft.Torch.Dynamic.Engine_x64.dll
set COMPLUS_ProfAPI_ProfilerCompatibilitySetting=EnableV2Profiler
set TORCH_CALLBACK_HOME=%ROOT%

set CORECLR_PROFILER={cf0d821e-299b-5307-a3d8-b283c03916dd}
set CORECLR_ENABLE_PROFILING=1
set CORECLR_PROFILER_PATH_32=%ROOT%\Microsoft.Torch.Dynamic.Engine_Win32.dll
set CORECLR_PROFILER_PATH_64=%ROOT%\Microsoft.Torch.Dynamic.Engine_x64.dll
set COMPLUS_ProfAPI_ProfilerCompatibilitySetting=EnableV2Profiler
set TORCHCORE_CALLBACK_HOME=%ROOT%

echo Profiler is On. Profiler paths are below:
echo Framework: %COR_PROFILER_PATH_64%
echo NetCore: %CORECLR_PROFILER_PATH_64%
