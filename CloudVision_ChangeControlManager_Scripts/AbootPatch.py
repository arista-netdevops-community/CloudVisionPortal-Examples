
import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)

#This script will install the Aboot patch for Field Notice 044
#The image can be downloaded from any server using https.  File source is defined in the YAML file
#If using CVP as source for the patch file, it requires that CVP has an image bundle containing that Aboot patch file in it
#If the installation is done over the none default VRF, change the VRF argument in the YAML config file

target = Device(ip)
cmdList = [ "enable" , "show hostname" ]
cmdResponse = target.runCmds(cmdList)
hostname = cmdResponse[1]['response']['hostname']
URL = scriptArgs["extension_URL"]
vrf = scriptArgs["VRF"]
extension = scriptArgs["extension"]

alog("Running installation Aboot patch from script on %s from %s over %s VRF" % (hostname, source, vrf))

target.runCmds(["cli vrf %s" % (vrf), "copy https:/%s%s extension:" % (URL, extension), "extension %s" % (extension)])
