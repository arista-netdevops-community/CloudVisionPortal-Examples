# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "json",
#     "requests",
#     "ssl",
# ]
# ///

# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import ssl
import requests
import json
from getpass import getpass

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Add the device registration token here if you want to (re)onboard devices.
# Leave it as None if you just want to change the TA configuration.
token = None

# Get the daemon configuration from Device Registration's main page (on CVaaS) or
# from the Onboard/Enroll with Certificates subpage (on-prem)
daemon_config = "COPY DAEMON TERMINATTR exec line from CV UI"

# Device list (copy and paste from exported inventory CSV)
devices = [
    "192.0.2.212",
    "192.0.2.213",
    "192.0.2.214",
    "192.0.2.215",
    "192.0.2.216",
    "192.0.2.217"
]

# Change below variables if needed. This must be a valid user on the devices.
username = "cvpadmin"
password = getpass("Enter password: ")

# JSON-RPC headers
headers = {
    "Content-Type": "application/json"
}

# Function to send JSON-RPC request
def send_rpc_request(device, commands):
    url = f"https://{device}/command-api"
    payload = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "params": {
            "version": 1,
            "cmds": commands,
            "format": "json"
        },
        "id": 1
    }
    
    try:
        response = requests.post(url, headers=headers, auth=(username, password), json=payload, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {device}: {e}")
        return None

# Run configuration commands on each device
for dev in devices:
    print(f"[INFO] Configuring {dev}...")

    if token is not None:
        token_path = "/tmp/cv-onboarding-token" if 'arista.io' in daemon_config else "/tmp/token"
        commands = [
            "enable",
            {"cmd": f"copy terminal: file:{token_path}", "input": token},
            "configure",
            "daemon TerminAttr",
            daemon_config,
            "shutdown",
            "no shutdown"
        ]
    else:
        commands = [
            "enable",
            "configure",
            "daemon TerminAttr",
            daemon_config,
            "shutdown",
            "no shutdown"
        ]

    result = send_rpc_request(dev, commands)

    if result:
        print(f"[SUCCESS] {dev} configured successfully!")
    else:
        print(f"[FAILURE] {dev} configuration failed!")

print("[INFO] Configuration complete.")