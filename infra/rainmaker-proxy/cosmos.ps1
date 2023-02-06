#Refernce: https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-command-line-parameters
#Clear cache
Remove-Variable * -ErrorAction SilentlyContinue; Remove-Module *; $error.Clear(); Clear-Host
#The emulator comes with a PowerShell module to start, stop, uninstall, and retrieve the status of the service. Run the following cmdlet to use the PowerShell module
Import-Module "$env:ProgramFiles\Azure Cosmos DB Emulator\PSModules\Microsoft.Azure.CosmosDB.Emulator"
#Start Emulator
Start-CosmosDbEmulator
