@echo off
set dllPath=%~dp0
set logPath=%dllPath%logs
IF NOT EXIST %logPath% mkdir %logPath%

echo [101;93m Note: Put the following under ^<ServiceManifest^>\^<CodePackage^> in the ServiceManifest.xml file [0m
echo Logs will be written to %logPath%
echo ===================================
rem env variable required by .NET runtime
echo ^<EnvironmentVariables^>

echo     ^<EnvironmentVariable Name="COR_ENABLE_PROFILING" Value="1"/^>
echo     ^<EnvironmentVariable Name="COR_PROFILER" Value="{cf0d821e-299b-5307-a3d8-b283c03916dd}"/^>
echo     ^<EnvironmentVariable Name="COR_PROFILER_PATH_32" Value="%dllPath%Microsoft.Torch.Dynamic.Engine_Win32.dll"/^>
echo     ^<EnvironmentVariable Name="COR_PROFILER_PATH_64" Value="%dllPath%Microsoft.Torch.Dynamic.Engine_x64.dll"/^>
echo     ^<EnvironmentVariable Name="COMPLUS_ProfAPI_ProfilerCompatibilitySetting" Value="EnableV2Profiler"/^>
echo     ^<EnvironmentVariable Name="TORCH_CALLBACK_HOME" Value="%dllPath%"/^>

echo     ^<EnvironmentVariable Name="CORECLR_ENABLE_PROFILING" Value="1"/^>
echo     ^<EnvironmentVariable Name="CORECLR_PROFILER" Value="{cf0d821e-299b-5307-a3d8-b283c03916dd}"/^>
echo     ^<EnvironmentVariable Name="CORECLR_PROFILER_PATH_32" Value="%dllPath%Microsoft.Torch.Dynamic.Engine_Win32.dll"/^>
echo     ^<EnvironmentVariable Name="CORECLR_PROFILER_PATH_64" Value="%dllPath%Microsoft.Torch.Dynamic.Engine_x64.dll"/^>
echo     ^<EnvironmentVariable Name="COMPLUS_ProfAPI_ProfilerCompatibilitySetting" Value="EnableV2Profiler"/^>
echo     ^<EnvironmentVariable Name="TORCHCORE_CALLBACK_HOME" Value="%dllPath%"/^>

rem env variables required by CLR IE
echo     ^<EnvironmentVariable Name="MicrosoftInstrumentationEngine_LogLevel" Value="Messages"/^>
echo     ^<EnvironmentVariable Name="MicrosoftInstrumentationEngine_FileLogPath" Value="%logPath%"/^>
echo     ^<EnvironmentVariable Name="MicrosoftInstrumentationEngine_ConfigPath64_1" Value="%dllPath%CLRProfiler_x64.config"/^>
echo     ^<EnvironmentVariable Name="MicrosoftInstrumentationEngine_ConfigPath32_1" Value="%dllPath%CLRProfiler_x86.config"/^>
echo     ^<EnvironmentVariable Name="MicrosoftInstrumentationEngine_DisableCodeSignatureValidation" Value="1"/^>

REM env var required by Torch"/^>
echo     ^<EnvironmentVariable Name="TORCHCORE_CALLBACK_HOME" Value="%dllPath%"/^>
echo     ^<EnvironmentVariable Name="TORCH_CALLBACK_HOME" Value="%dllPath%"/^>
echo     ^<EnvironmentVariable Name="TORCH_DYNAMIC_MessageboxAtAttach" Value="0"/^>

echo ^</EnvironmentVariables^>
echo ===================================
