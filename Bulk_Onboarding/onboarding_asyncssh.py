# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "asyncssh",
# ]
# ///

# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import argparse
import asyncio
import asyncssh
from getpass import getpass

def parse_args():
    parser = argparse.ArgumentParser(
        description="Configure TerminAttr on Arista devices via SSH."
    )
    parser.add_argument(
        "--devices",
        required=True,
        type=lambda s: [d.strip() for d in s.split(",")],
        metavar="IP1,IP2,...",
        help="Comma-separated device IPs or hostnames (e.g. --devices 192.0.2.1,192.0.2.2)",
    )
    parser.add_argument(
        "--token",
        default=None,
        metavar="TOKEN",
        help="Device registration token for (re)onboarding. Omit to only update TA config.",
    )
    parser.add_argument(
        "--terminattr-config",
        default=None,
        metavar="CONFIG",
        help="TerminAttr exec line from the CV UI. Required to apply or update TA config.",
    )
    return parser.parse_args()


async def configure_device(device, commands, username, password):
    try:
        async with asyncssh.connect(
            device,
            username=username,
            password=password,
            known_hosts=None,
        ) as conn:
            stdin, stdout, _ = await conn.open_session(term_type="dumb")

            await asyncio.sleep(1)

            for cmd in commands:
                stdin.write(cmd + "\n")
                await asyncio.sleep(0.5)

            await asyncio.sleep(2)
            output = await asyncio.wait_for(stdout.read(65535), timeout=5)
            return output
    except Exception as e:
        print(f"[ERROR] {device}: {e}")
        return None


async def main():
    args = parse_args()
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    if args.token is None:
        print("[ERROR] At least one of --token")
        return

    commands = ["enable"]

    if args.token is not None:
        token_path = "/tmp/cv-onboarding-token" if args.terminattr_config and "arista.io" in args.terminattr_config else "/tmp/token"
        commands += [
            f"copy terminal: file:{token_path}",
            args.token,
            "\x04",
        ]

    if args.terminattr_config is not None:
        commands += [
            "configure",
            "daemon TerminAttr",
            args.terminattr_config,
            "shutdown",
            "no shutdown",
            "write memory",
        ]
    elif args.terminattr_config is None:
        commands += [
            "configure",
            "daemon TerminAttr",
            "shutdown",
            "no shutdown"
        ]

    tasks = {dev: asyncio.create_task(configure_device(dev, commands, username, password)) for dev in args.devices}

    for dev, task in tasks.items():
        print(f"[INFO] Configuring {dev}...")
        result = await task
        if result is not None:
            print(f"[SUCCESS] {dev} configured successfully!")
        else:
            print(f"[FAILURE] {dev} configuration failed!")

    print("[INFO] Configuration complete.")


asyncio.run(main())
