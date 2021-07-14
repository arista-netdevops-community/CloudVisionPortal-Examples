#!/usr/bin/env python
#
# Copyright (c) 2021, Arista Networks
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
CCM Script - Check interfaces status and fail if specific interfaces are down

Notes -
Global Variables available to script using cvplibrary
   CVP_USERNAME - Username of the current user
   CVP_PASSWORD - Password of the current user
   CVP_IP - IP address of the current device
   CVP_MAC - MAC of the current device
   CVP_SERIAL - Serial number of the current device
   CVP_SESSION_ID - Session id of current cvp user, this can be passed around to cvp api
   SCRIPT_ARGS - A dictionary of arguments passed to the Script Action configured in associated yaml file

Audit Logging function
   alog(string) - alog function writes the string to the audit logs tagged with the specific change control
   calling the script

Required Arguments
   interfaces - list of interfaces on EOS

Sample yaml file
    name: intf-check
    args:
       interfaces: "Ethernet1,Ethernet3"

"""
# Import required Librarys
import json
import re
from cvplibrary.auditlogger import alog # CVP auit log function
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames # CVP Variables

# Create Script variables
ipAddress = CVPGlobalVariables.getValue( GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue( GlobalVariableNames.SCRIPT_ARGS)

# Write entry to Log
alog("running show interfaces status to check if any important interfaces are down")
# Connect to Device specified in Change Control
switch = Device(ipAddress)
# Run show commands on the switch
data = switch.runCmds(["enable","show interfaces status"])

down = []
downCtr = 0
up = []
upCtr = 0

interfaces = re.split(',', scriptArgs['interfaces'])

for interface in interfaces:
   intf = data[1]['response']['interfaceStatuses'][interface]
   if intf['lineProtocolStatus'] == 'up' and intf['linkStatus'] == 'connected':
      upCtr += 1
      up.append(interface)
   else:
      downCtr += 1
      down.append(interface)
if len(up) == len(interfaces):
   alog("All interfaces are up. Proceeding with task execution...")
elif downCtr > 0:
   down = ' '.join([str(elem) for elem in down])
   alog("Interface(s) in down state: {}".format(str(down)))
   assert(False)
