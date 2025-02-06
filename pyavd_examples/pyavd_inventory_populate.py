#!/usr/bin/python3

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyavd",
#     "pyyaml",
# ]
# [tool.uv]
# exclude-newer = "2024-08-05T00:00:00Z"
# ///

# Copyright (c) 2023-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations
import asyncio
import yaml

from pyavd._cv.client import CVClient
from pyavd._cv.client.exceptions import CVClientException

from pyavd._cv.workflows.models import (
    CloudVision,
    DeployToCvResult,
)

import argparse
import logging

async def get_inventory(
    cloudvision: CloudVision,
) -> DeployToCvResult:

    try:
        async with CVClient(servers=cloudvision._servers, token=cloudvision._token, verify_certs=cloudvision._verify_certs) as cv_client:

            try:

                logging.info("Get devices ...")
                inventory = await cv_client.get_inventory_devices()
                result = [
                    {
                        'hostname': device.hostname,
                        'serialNumber': device.key.device_id
                    }
                    for device in inventory
                ]

            except CVClientException as e:
                logging.info(e)

    except CVClientException as e:
        logging.info(e)

    for device in result:
        if device["hostname"]:
            with open(f"structured_configs/{device['hostname']}.yaml", "w") as f:
                f.write(yaml.dump({"hostname": device["hostname"], "serial_number": device["serialNumber"], "is_deployed": True}, default_flow_style=False))

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pushes Static Configlets to CloudVision using Static Config Studios"
    )
    parser.add_argument(
        "--token-file",
        required=True,
        metavar="token_file",
        help="Location on disk for service account token",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "--apiserver",
        required=True,
        metavar="www.arista.io",
        dest="apiserver_url",
        help="endpoint for CVP/CVaaS cluster (must be the www endpoint)",
    )
    parser.add_argument(
        "--log-level",
        required=False,
        metavar="LOGLEVEL",
        help="Logging level for output. This can be any standard Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Only the DEBUG and INFO levels are used in this script at present.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        type=str,
        default="INFO",
    )
    args = parser.parse_args()

    # setup logging level from args and do initial debug logging
    logging.basicConfig(level=args.log_level)
    logging.info("Script starting")
    logging.debug("Arguments parsed")
    logging.debug(args)

    token = args.token_file.read().strip()
    CloudVision = CVClient(servers=args.apiserver_url,token=token, verify_certs=False)

    asyncio.run(get_inventory(cloudvision=CloudVision))
