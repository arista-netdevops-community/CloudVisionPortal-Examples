from cvplibrary.auditlogger import alog # CVP auit log function
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames # CVP Variables

# Create Script variables
ipAddress = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue( GlobalVariableNames.SCRIPT_ARGS)

# collect arguments from YAML
token = scriptArgs["token"]
filename = scriptArgs["filename"]

# Write entry to Log
alog("Uploading onboarding token..")

# Connect to Device specified in Change Control
switch = Device(ipAddress)

# download EOS
data = switch.runCmds(["enable", {"cmd": "copy terminal: file:{}".format(filename),"input": token}])