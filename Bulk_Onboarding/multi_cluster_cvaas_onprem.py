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
with open("cvaas.tok") as f:
    token = f.read().strip('\n')

with open("onprem.tok") as f:
    token2 = f.read().strip('\n')

# CVaaS #1
clnt = CvpClient()
clnt.connect(nodes=['www.arista.io'], username='',password='',is_cvaas=True, api_token=token)

cvaas_token = clnt.api.create_enroll_token('720h')[0]['enrollmentToken']['token']


# On-prem #1
primary = CvpClient()
primary.connect(nodes=['192.0.2.79'], username='',password='',is_cvaas=False, api_token=token2)

primary_token = primary.api.create_enroll_token('720h')['data']


#Device list
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

# streaming to CVaaS and on-prem
for dev in devices:
    sw = jsonrpclib.Server(f"https://{username}:{password}@{dev}/command-api", context=context)
    sw.runCmds(1,[
        "enable",
        {"cmd": "copy terminal: file:/tmp/token", "input": primary_token['data']},
        {"cmd": "copy terminal: file:/tmp/cv-onboarding-token", "input": cvaas_token[0]['enrollmentToken']['token']},
        "configure",
        "daemon TerminAttr",
        "exec /usr/bin/TerminAttr -cvopt cvaas.addr=apiserver.arista.io:443 -cvopt cvaas.auth=token-secure,/tmp/cv-onboarding-token -cvopt cvaas.vrf=MGMT -cvopt onprem.addr=192.0.2.779:9910,192.0.2.78:9910,192.0.2.79:9910 -cvopt onprem.auth=token,/tmp/token -cvopt onprem.vrf=MGMT -cvopt -taillogs",
        "shutdown",
        "no shutdown"
    ])
