import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)

# This script can be used to migrate nodes from CVP on-prem to CVaaS
# An onboarding token needs to be generated on CVaaS and defined in the argument in the YAML file

target = Device(ip)
TOKEN = scriptArgs["Token"]
VRF = scriptArgs["VRF"]

# Write an entry to CVP Log
alog("Migrating node to CVaaS")

# Migration
try:
    target.runCmds(["enable", \
      {"cmd": "copy terminal: file:/tmp/cv-onboarding-token", "input": TOKEN}, \
     "configure", \
     "daemon TerminAttr", \
     "exec /usr/bin/TerminAttr -cvaddr=apiserver.arista.io:443 -cvcompression=gzip -cvvrf=%s -taillogs -cvauth=token-secure,/tmp/cv-onboarding-token -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent" % (VRF), \
     "no shutdown"])
except:
    alog("Migration failed")
else:
    alog("Migration succeded")
