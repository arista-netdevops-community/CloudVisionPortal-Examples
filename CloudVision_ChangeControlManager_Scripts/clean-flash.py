import json
import re
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
serial = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SERIAL)
session_id = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SESSION_ID)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)
alog("Remove all old EOSs from /mnt/flash")

switch = Device(ip)
# Get current boot image
cmdOut = switch.runCmds(["show boot"])
eosBootImageFull = cmdOut[0]["response"]["softwareImage"]
eosBootImage = eosBootImageFull.split("/")[1]

cmdOut = switch.runCmds(["dir flash:EOS*"])
eosListTxt = cmdOut[0]["response"]["messages"][0]
eosList = re.findall(r'EOS.*\.swi', eosListTxt)

for eos in eosList:
    if eos != eosBootImage:
        cmd = "delete flash:" + eos
        cmdOut = switch.runCmds([cmd])