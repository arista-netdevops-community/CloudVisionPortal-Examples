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

from pyavd._cv.client import CVClient
from pyavd._cv.client.exceptions import CVClientException

from pyavd._cv.workflows.create_workspace_on_cv import create_workspace_on_cv
from pyavd._cv.workflows.deploy_configs_to_cv import deploy_configs_to_cv
from pyavd._cv.workflows.deploy_studio_inputs_to_cv import deploy_studio_inputs_to_cv
from pyavd._cv.workflows.finalize_change_control_on_cv import finalize_change_control_on_cv
from pyavd._cv.workflows.finalize_workspace_on_cv import finalize_workspace_on_cv
from pyavd._cv.workflows.models import (
    CloudVision,
    CVChangeControl,
    CVDeviceTag,
    CVDevice,
    CVEosConfig,
    CVInterfaceTag,
    CVStudioInputs,
    CVWorkspace,
    DeployToCvResult,
)
from pyavd._cv.workflows.verify_devices_on_cv import verify_devices_on_cv

import argparse
import logging

async def deploy_to_cv(
    cloudvision: CloudVision,
    workspace: CVWorkspace | None = None,
    change_control: CVChangeControl | None = None,
    configs: list[CVEosConfig] | None = None,
    device_tags: list[CVDeviceTag] | None = None,
    interface_tags: list[CVInterfaceTag] | None = None,
    studio_inputs: list[CVStudioInputs] | None = None,
    skip_missing_devices: bool = False
) -> DeployToCvResult:

    logging.info("deploy_to_cv:")
    result = DeployToCvResult(workspace=workspace or CVWorkspace(), change_control=change_control)
    if device_tags is None:
        device_tags = []
    if interface_tags is None:
        interface_tags = []
    if configs is None:
        configs = []
    if studio_inputs is None:
        studio_inputs = []
    try:
        async with CVClient(servers=cloudvision._servers, token=cloudvision._token, verify_certs=cloudvision._verify_certs) as cv_client:
            logging.info("Creating workspace")
            await create_workspace_on_cv(workspace=result.workspace, cv_client=cv_client)

            try:
                logging.info("Verify devices on CV")
                await verify_devices_on_cv(
                    devices=(
                        [tag.device for tag in device_tags if tag.device is not None]
                        + [tag.device for tag in interface_tags if tag.device is not None]
                        + [config.device for config in configs if config.device is not None]
                    ),
                    workspace_id=result.workspace.id,
                    skip_missing_devices=skip_missing_devices,
                    warnings=result.warnings,
                    cv_client=cv_client,
                )

                logging.info("Deploy configs")
                await deploy_configs_to_cv(
                    configs=configs,
                    result=result,
                    cv_client=cv_client,
                )

                logging.info("Deploy studio inputs")
                await deploy_studio_inputs_to_cv(
                    studio_inputs=studio_inputs,
                    result=result,
                    cv_client=cv_client,
                )

            except CVClientException as e:
                result.errors.append(e)
                result.failed = True

            logging.info("Finalizing workspace")
            if result.failed:
                await cv_client.abandon_workspace(workspace_id=result.workspace.id)
                result.workspace.state = "abandoned"
                return result

            await finalize_workspace_on_cv(workspace=result.workspace, cv_client=cv_client)

            logging.info("Create/update change control")
            if result.workspace.change_control_id is not None:
                if result.change_control is None:
                    result.change_control = CVChangeControl()
                result.change_control.id = result.workspace.change_control_id

            if result.change_control is not None and result.change_control.id is not None:
                await finalize_change_control_on_cv(change_control=result.change_control, cv_client=cv_client)

    except CVClientException as e:
        result.errors.append(e)
        result.failed = True

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
        metavar="www.arista.io|192.0.2.10",
        dest="apiserver_url",
        help="endpoint for CVP on-prem cluster or CVaaS tenant (must be the www endpoint in case of CVaaS)",
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
    parser.add_argument(
        "--cc",
        required=True,
        metavar="cc",
        help="Change control state state: ('pending approval', 'approved', 'running', 'completed', 'deleted', 'failed')",
        default='pending approval',
        type=str,
    )
    args = parser.parse_args()

    # setup logging level from args and do initial debug logging
    logging.basicConfig(level=args.log_level)
    logging.info("Script starting")
    logging.debug("Arguments parsed")
    logging.debug(args)

    token = args.token_file.read().strip()
    CloudVision = CVClient(servers=args.apiserver_url,token=token, verify_certs=False)

    # Define the device inventory
    device_inventory =  [
        {
            "hostname": "tp-avd-spine1",
            "ip": "192.0.2.212",
            "serial_number": "CD0EADBEEA126915EA78E0FB4DC776CA",
            "system_mac_address": "50:08:00:8b:ee:b1"
        },
        {
            "hostname": "tp-avd-spine2",
            "ip": "192.0.2.213",
            "serial_number": "2568DB4A33177968A78C4FD5A8232159",
            "system_mac_address": "50:08:00:8c:22:49"
        },
        {
            "hostname": "tp-avd-leaf1",
            "ip": "192.0.2.214",
            "serial_number": "BAD032986065E8DC14CBB6472EC314A6",
            "system_mac_address": "50:08:00:a7:ca:c3"
        },
        {
            "hostname": "tp-avd-leaf2",
            "ip": "192.0.2.215",
            "serial_number": "0123F2E4462997EB155B7C50EC148767",
            "system_mac_address": "50:08:00:b1:5b:0b"
        },
        {
            "hostname": "tp-avd-leaf3",
            "ip": "192.0.2.216",
            "serial_number": "8520AF39790A4EC959550166DC5DEADE",
            "system_mac_address": "50:08:00:60:c6:76"
        },
        {
            "hostname": "tp-avd-leaf4",
            "ip": "192.0.2.217",
            "serial_number": "6323DA7D2B542B5D09630F87351BEA41",
            "system_mac_address": "50:08:00:25:9d:36"
        }
    ]

    # Create a list of CVEosConfig objects that contain the path to the config files and the device information
    configlets = [
        CVEosConfig(file=f"/home/avd/gitlab/avd-evpn-l3ls-v3/intended/configs/{host['hostname']}.cfg", device=CVDevice(hostname=f"{host['hostname']}", serial_number=f"{host['serial_number']}", system_mac_address=f"{host['system_mac_address']}", _exists_on_cv=True))
        for host in device_inventory
    ]

    change= CVChangeControl(requested_state=args.cc)

    asyncio.run(deploy_to_cv(cloudvision=CloudVision,configs=configlets,change_control=change))
