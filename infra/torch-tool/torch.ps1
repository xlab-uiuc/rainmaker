# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

<#
.SYNOPSIS
    This script spawns a process with the COR_PROFILER environment variables set. 

.PARAMETER ApplicationPath
    Optional, the application to run with the profiler set. By default, will spawn another PowerShell process.

#>

[CmdletBinding(DefaultParameterSetName='None')]
param(
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string]
    $ApplicationPath = "Write-Host 'This shell has Torch enabled, but no command is given to execute here. Use torch.ps1 <command>'; pause"
)

# CLRIE configuration variables
$configurationEnvironmentVariables = @(
    # COR_PROFILER
    @{
        name   = 'COR_ENABLE_PROFILING'
        value  = 1
        enable = $true
    }
    @{
        name   = 'COR_PROFILER'
        value  = '{cf0d821e-299b-5307-a3d8-b283c03916dd}'
        enable = $true
    }
    @{
        name   = 'COR_PROFILER_PATH_32'
        value  = $PSScriptRoot + "\Microsoft.Torch.Dynamic.Engine_Win32.dll"
        enable = $true
    }
    @{
        name   = 'COR_PROFILER_PATH_64'
        value  = $PSScriptRoot + "\Microsoft.Torch.Dynamic.Engine_x64.dll"
        enable = $true
    }
    @{
        name   = 'CORECLR_ENABLE_PROFILING'
        value  = 1
        enable = $true
    }
    @{
        name   = 'CORECLR_PROFILER'
        value  = '{cf0d821e-299b-5307-a3d8-b283c03916dd}'
        enable = $true
    }
    @{
        name   = 'CORECLR_PROFILER_PATH_32'
        value  = $PSScriptRoot + "\Microsoft.Torch.Dynamic.Engine_Win32.dll"
        enable = $true
    }
    @{
        name   = 'CORECLR_PROFILER_PATH_64'
        value  = $PSScriptRoot + "\Microsoft.Torch.Dynamic.Engine_x64.dll"
        enable = $true
    }
    @{
        name   = 'COMPLUS_ProfAPI_ProfilerCompatibilitySetting'
        value  = "EnableV2Profiler"
        enable = $true
    }
    @{
        name   = 'TORCH_CALLBACK_HOME'
        value  = $PSScriptRoot
        enable = $true
    }
    @{
        name   = 'TORCHCORE_CALLBACK_HOME'
        value  = $PSScriptRoot
        enable = $true
    }    
    @{
        name   = 'TORCH_DYNAMIC_MessageboxAtAttach'
        value  = 0
        enable = $true
    }
)

$configurationEnvironmentVariables | ForEach-Object {
    $envVarPath = "Env:\$($_.name)"
    if ($_.enable) {
        Write-Verbose "Set $($_.name) = $($_.value)"
        New-Item -Path $envVarPath -Value $_.value -Force | Out-Null
    } elseif (Test-Path $envVarPath) {
        Write-Verbose "Removed $($_.name)"
        Remove-Item -Path $envVarPath
    }
}

Start-Process powershell -ArgumentList "-noexit", "-noprofile", "-command $ApplicationPath"

# This reverts the state of the caller to not be profiled
$configurationEnvironmentVariables | ForEach-Object {
    $envVarPath = "Env:\$($_.name)"
    if (Test-Path $envVarPath) {
        Write-Verbose "Removed $($_.name)"
        Remove-Item -Path $envVarPath
    }
}