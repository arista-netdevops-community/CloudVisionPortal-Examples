# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from cvprac.cvp_client import CvpClient
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import jsonrpclib
from getpass import getpass

############ Generating tokens #################
# Reading the service account token from a file
with open("primary.tok") as f:
    token = f.read().strip('\n')

with open("standby.tok") as f:
    token2 = f.read().strip('\n')

# On-prem #1
primary = CvpClient()
primary.connect(nodes=['192.0.2.79'], username='',password='', api_token=token)

primary_token = primary.api.create_enroll_token('720h')['data']

# On-prem #2
standby = CvpClient()
standby.connect(nodes=['192.0.2.200'], username='',password='', api_token=token2)

standby_token = standby.api.create_enroll_token('720h')['data']

# Device list
devices = [
    "192.0.2.212",
    "192.0.2.213",
    "192.0.2.214",
    "192.0.2.215",
    "192.0.2.216",
    "192.0.2.217"
]

# Change below variables to match your environment
username = "arista"
password = getpass("Enter password: ")

# Use TLSv1.2
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
# Using the EOS default ciphers
context.set_ciphers('AES256-SHA:DHE-RSA-AES256-SHA:AES128-SHA:DHE-RSA-AES128-SHA')

# streaming to standby. and on-prem
for dev in devices:
    sw = jsonrpclib.Server(f"https://{username}:{password}@{dev}/command-api", context=context)
    sw.runCmds(1,[
        "enable",
        {"cmd": "copy terminal: file:/tmp/token", "input": primary_token['data']},
        {"cmd": "copy terminal: file:/tmp/standby-token", "input": standby_token['data']},
        "configure",
        "daemon TerminAttr",
        "exec /usr/bin/TerminAttr  -cvopt primary.addr=192.0.2.779:9910,192.0.2.78:9910,192.0.2.79:9910 -cvopt primary.auth=token,/tmp/token -cvopt primary.vrf=MGMT -cvopt standby.addr=192.0.2.200:9910,192.0.2.201:9910,192.0.2.202:9910 -cvopt standby.auth=token-secure,/tmp/standby-token -cvopt standby.vrf=MGMT -taillogs",
        "shutdown",
        "no shutdown"
    ])
