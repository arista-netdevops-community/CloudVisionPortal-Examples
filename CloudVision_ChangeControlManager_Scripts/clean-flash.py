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
cmdOut = switch.runCmds(["enable","show boot"])
eosBootImageFull = cmdOut[1]["response"]["softwareImage"]
eosBootImage = eosBootImageFull.split("/")[1]

cmdOut = switch.runCmds(["enable","dir flash:EOS*"])
eosListTxt = cmdOut[1]["response"]["messages"][0]
eosList = re.findall(r'EOS.*\.swi', eosListTxt)

deleted = []
for eos in eosList:
    if eos != eosBootImage:
        cmd = "delete flash:" + eos
        cmdOut = switch.runCmds(["enable", cmd])
        deleted.append(eos)

deleted = ' '.join([str(elem) for elem in deleted])
alog("The following images were removed to free up space: {}".format(deleted))
