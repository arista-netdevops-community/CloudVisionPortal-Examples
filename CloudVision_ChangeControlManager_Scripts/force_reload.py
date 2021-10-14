# !/usr/bin/env python
"""
Description - Force reloads a device and runs connectivity checks via eAPI calls until it comes back up.
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
   CHECK_INTERVAL - how long to wait between running eAPI checks to the device
   MAX_CHECK_COUNT - maximum number of check cycles to run before failing the task
Smaple yaml file
   name: Force Reload
   args:
     CHECK_INTERVAL: 10
     MAX_CHECK_COUNT: 120
"""
# import required CVP libraries
from cvplibrary.auditlogger import alog  # CVP audit log function
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames  # CVP Variables
from cvplibrary.request_session import RequestSession
from cvpServices import CvpError

# import standard Python libraries
import time

# Pull in data from task and YAML variables
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)
CHECK_INTERVAL = int(scriptArgs['CHECK_INTERVAL'])
MAX_CHECK_COUNT = int(scriptArgs['MAX_CHECK_COUNT'])
ip_address = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
serial = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SERIAL)


def reload(addr):
    commands = ['enable',
                'reload now']

    switch = Device(addr)
    switch.runCmds(commands)


def liveness_check(addr):
    """
    Ping requires root access, which this script will not have when running in the executor container.
    We also cannot query aeris for device streaming state on older versions of CVP, so here we send a simple request
    repeatedly to the device EAPI socket and see if we get a response or not. If we do, the device is back online.
    """
    commands = ['show version']
    switch = Device(addr)

    try:
        # if the switch sends us any response, it's up
        switch.runCmds(commands)
        return True
    except CvpError:
        return False


def msg_out(test, message):
    """ Output log messages to stdout if testing
      or CVP CC log if running in CVP
    """
    if test:
        print(message)
    else:
        alog(message)


# Check to see if this script is being tested or run in CVP
if not RequestSession.getSessionId():
    test = True
else:
    test = False

msg_out(test, 'Reloading {} now'.format(serial))
reload(ip_address)
msg_out(test, '{} has been reloaded, monitoring via eAPI calls for device to come back up'.format(serial))

# do a 20 second sleep here to give the device time to go down, otherwise you can hit a scenario where you issue the
# 'reload now' command, the script immediately fires off the eAPI call, and it succeeds before the device goes down
# ruining the point of checking device liveness via eAPI calls
time.sleep(20)

for i in range(MAX_CHECK_COUNT):
    if liveness_check(ip_address):
        msg_out(test, '{} ({}) is responding again, terminating task after 5 second grace period'.format(ip_address,
                                                                                                         serial))
        # 5 second grace period used to allow SSH process to come online after device starts responding to eAPI calls
        # again, if we've caught it just as the device has come up
        time.sleep(5)
        break
    else:
        msg_out(test,
                'Liveness check {} of {} - {} ({}) is not responding yet'.format(i + 1, MAX_CHECK_COUNT, ip_address,
                                                                                 serial))
        time.sleep(CHECK_INTERVAL)
else:  # else clause on a for-loop in python fires if the entire for loop completes without break
    msg_out(test, "{} ({}) failed to respond. Retry count exhausted.".format(ip_address, serial))
    raise UserWarning("{} ({}) failed to respond. Retry count exhausted.".format(ip_address, serial))
