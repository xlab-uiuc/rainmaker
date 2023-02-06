# Go to default Azurite location. This may cause problem if users do not use default intall location
cd "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\Extensions\Microsoft\Azure Storage Emulator"
# Clear cache of powershell in order to solve Azurite stuck problems. Unitil now, it works.
Remove-Variable * -ErrorAction SilentlyContinue; Remove-Module *; $error.Clear(); Clear-Host
# Start Azurite blob queue and table in three new ports.
.\azurite.exe --blobPort 20000 --queuePort 20001 --tablePort 20002
