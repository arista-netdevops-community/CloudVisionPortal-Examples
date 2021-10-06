import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)

target = Device(ip)

lastoctet = ip.split(".")[3]

cmdList = [ "enable" , "show hostname" ]
cmdResponse = target.runCmds(cmdList)
hostname = cmdResponse[1]['response']['hostname']

alog("Running installation of EOS 4.24.4M from script on %s" % (hostname))

if int(lastoctet) % 2 == 0 :
	target.runCmds(["cli vrf MGMT", "install source https://10.169.44.133/cvpservice/image/getImagebyId/EOS-4.24.4M.swi reload now"])
	alog("Installing EOS 4.24.4M on %s" % (hostname))
else :
	alog("Skipping EOS 4.24.4M install because this device %s ip %s is not an even number" % (hostname, ip))