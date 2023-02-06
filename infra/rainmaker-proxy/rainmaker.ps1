# Start-Process powershell -Verb runAs -ArgumentList "-noexit", "-file emulator.ps1"
# PowerShell -Verb runAs -NoExit ".\emulator.ps1"
# pushd
# cd "..\torch-tool"
# $myprocss = Start-Process powershell -Verb runAs -PassThru -Wait -ArgumentList "-NoExit", "-File emulator.ps1"
# $myprocss.WaitForExit()

# popd
# Start-Process powershell -Verb runAs -ArgumentList "-noexit -file emulator.ps1"
mvn package
java -jar .\target\rainmaker-proxy-1.0-SNAPSHOT.jar -Xmx8g
# pushd
# cd "..\torch-tool"
# Start-Process powershell -Verb runAs -ArgumentList "-noexit -file ProfOff.ps1"
# popd