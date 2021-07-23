from cvplibrary.auditlogger import alog # CVP auit log function
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames # CVP Variables

# Create Script variables
ipAddress = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue( GlobalVariableNames.SCRIPT_ARGS)

# collect arguments from YAML
URL = scriptArgs["REPO"]
vrf = scriptArgs["VRF"]
EOS = scriptArgs["EOS"]

# Write entry to Log
alog("Downloading EOS image from CVP")

# Connect to Device specified in Change Control
switch = Device(ipAddress)

# download EOS
data = switch.runCmds(["enable","cli vrf %s" % (vrf),"copy https:/%s%s flash:" % (URL, EOS)])
