# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import ssl
from getpass import getpass
ssl._create_default_https_context = ssl._create_unverified_context
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import jsonrpclib
from getpass import getpass


token = "<INSERT DEVICE REGISTRATION TOKEN HERE>"

# Get the daemon configuration from Device Registration's main page (on CVaaS) or
# from the Onboard/Enroll with Certificates subpage (on-prem)
daemon_config = "COPY DAEMON TERMINATTR exec line from CV UI"

# Device list (copy and paste from exported inventory CSV
devices = [
    "192.0.2.212",
    "192.0.2.213",
    "192.0.2.214",
    "192.0.2.215",
    "192.0.2.216",
    "192.0.2.217"
]

# Change below variables
username = "cvpadmin"
password = getpass("Enter password: ")

# Use TLSv1.2
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
# Using the EOS default ciphers
context.set_ciphers('AES256-SHA:DHE-RSA-AES256-SHA:AES128-SHA:DHE-RSA-AES128-SHA')

if 'arista.io' in daemon_config:
    token_path = "/tmp/cv-onboarding-token"
else:
    token_path = "/tmp/token"
for dev in devices:
    sw = jsonrpclib.Server(f"https://{username}:{password}@{dev}/command-api", context=context)
    sw.runCmds(1,[
        "enable",
        {"cmd": f"copy terminal: file:{token_path}", "input": token},
        "configure",
        "daemon TerminAttr",
        daemon_config,
        "shutdown",
        "no shutdown"
    ])
