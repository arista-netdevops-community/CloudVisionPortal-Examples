#!/usr/bin/python3

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyavd",
#     "pyyaml",
# ]
# [tool.uv]
# exclude-newer = "2025-07-15T00:00:00Z"
# ///

# Copyright (c) 2023-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from __future__ import annotations
import asyncio
import json
import yaml
from pyavd._cv.api.arista.studio.v1 import (
    Inputs,
    InputsKey,
    InputsServiceStub,
    InputsStreamRequest,
)
from pyavd._cv.api.arista.configlet.v1 import (
    Configlet,
    ConfigletKey,
    ConfigletAssignment,
    ConfigletAssignmentKey,
    ConfigletAssignmentServiceStub,
    ConfigletAssignmentStreamRequest,
    ConfigletStreamRequest,
    ConfigletServiceStub,
    Filter
)

import argparse
import logging
import pyavd
from pyavd._cv.client import CVClient
from pyavd._cv.client.exceptions import CVClientException

async def get_studio_inputs_all(
        CVClient,
        time: datetime | None = None,
        timeout: float = 600,
    ) -> Any:
        """

        Parameters:
            time: Timestamp from which the information is fetched. `now()` if not set.
            timeout: Timeout in seconds.
        Returns:
            A list of dictionaries that contains the studio ID and the inputs of each studio.
        """
        request = InputsStreamRequest(partial_eq_filter=[
                Inputs(
                    key=InputsKey(workspace_id=""),
                ),
            ],
            time=time
        )
        client = InputsServiceStub(CVClient._channel)
        studio_inputs = []
        try:
            responses = client.get_all(request, metadata=CVClient._metadata, timeout=timeout)
            async for response in responses:
                if response.value.inputs is None:
                    continue
                studio_inputs.append({"studio_id": response.value.key.studio_id, "inputs": {"path":[],"inputs": json.loads(response.value.inputs)}})
        except Exception as e:
            print(e)

        return studio_inputs

async def get_configlet_containers(
    CVClient,
    workspace_id: str,
    container_ids: list[str] | None = None,
    timeout: float = 600,
) -> list[ConfigletAssignment]:
    """
    Get Configlet Containers (a.k.a. Assignments) using arista.configlet.v1.ConfigletAssignmentServiceStub.GetAll API.

    Parameters:
        workspace_id: Unique identifier of the Workspace for which the information is fetched. Use "" for mainline.
        container_ids: Unique identifiers for Containers/Assignments.
        timeout: Timeout in seconds.

    Returns:
        ConfigletAssignment objects.
    """
    request = ConfigletAssignmentStreamRequest(partial_eq_filter=[])
    if container_ids:
        for container_id in container_ids:
            request.partial_eq_filter.append(
                ConfigletAssignment(key=ConfigletAssignmentKey(workspace_id=workspace_id, configlet_assignment_id=container_id)),
            )
    else:
        request.partial_eq_filter.append(ConfigletAssignment(key=ConfigletAssignmentKey(workspace_id=workspace_id)))

    client = ConfigletAssignmentServiceStub(CVClient._channel)

    responses = client.get_all(request, metadata=CVClient._metadata, timeout=timeout)
    configlet_assignments = [response.value async for response in responses]


    return configlet_assignments

async def get_configlets(
        CVClient,
        workspace_id: str,
        configlet_ids: list[str] | None = None,
        timeout: float = 600,
    ) -> list[Configlet]:
        """
        Get Configlets using arista.configlet.v1.ConfigletServiceStub.GetAll API.

        Missing objects will not produce an error.

        Parameters:
            workspace_id: Unique identifier of the Workspace for which the information is fetched. Use "" for mainline.
            configlet_ids: Unique identifiers for Configlets. If not set the function will return all configlets.
            timeout: Timeout in seconds.

        Returns:
            List of matching Configlet objects.
        """
        request = ConfigletStreamRequest(partial_eq_filter=[],filter=Filter(include_body=True))
        if configlet_ids:
            for configlet_id in configlet_ids:
                request.partial_eq_filter.append(Configlet(key=ConfigletKey(workspace_id=workspace_id, configlet_id=configlet_id)))
        else:
            request.partial_eq_filter.append(Configlet(key=ConfigletKey(workspace_id=workspace_id)))

        client = ConfigletServiceStub(CVClient._channel)

        responses = client.get_all(request, metadata=CVClient._metadata, timeout=timeout)
        configlets = [response.value async for response in responses]

        return configlets

async def backup_studios(cloudvision: CloudVision):
    async with CloudVision as cv_client:
        result = await get_studio_inputs_all(cv_client)
        # Static Config Studio is special and we need to get the configlets, configlet assignments in addition to
        # the studio inputs that only contain the configletAssignmentRoots
        configlets = await get_configlets(cv_client, workspace_id="",configlet_ids=[])
        configlet_list = []
        for configlet in configlets:
            configlet_dict = {
                "configletId": configlet.key.configlet_id,
                "digest": configlet.digest,
                "body": configlet.body,
                "description": configlet.description,
                "displayName": configlet.display_name,
            }
            configlet_list.append(configlet_dict)
        assignments = await get_configlet_containers(cv_client, workspace_id="", container_ids=[])
        assignment_list = []
        for assignment in assignments:
            configlet_dict = {
                "configletAssignmentId": assignment.key.configlet_assignment_id,
                "query": assignment.query,
                "description": assignment.description,
                "displayName": assignment.display_name,
                "configletIds": assignment.configlet_ids.values,
                "childAssignmentIds": assignment.child_assignment_ids.values,
                "matchPolicy": assignment.match_policy.value,
            }
            assignment_list.append(configlet_dict)
        # Loop through the studios and dump the inputs to a yaml file
        for studio in result:

            if studio['studio_id'] == "studio-static-configlet":
                studio['inputs']['inputs']['configletAssignments'] = assignment_list
                studio['inputs']['inputs']['configlets'] = configlet_list
            logging.info(f"Backing up studio {studio['studio_id']}")
            with open(f"{studio['studio_id']}.yaml", "w") as f:
                yaml.dump(studio['inputs'], f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup Studio inputs"
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

    args = parser.parse_args()

    # setup logging level from args and do initial debug logging
    logging.basicConfig(level=args.log_level)
    logging.info(f"Using pyavd version: {pyavd.__version__}")
    logging.info("Script starting")
    logging.debug("Arguments parsed")
    logging.debug(args)

    token = args.token_file.read().strip()
    CloudVision = CVClient(servers=args.apiserver_url,token=token, verify_certs=False)
    asyncio.run(backup_studios(CloudVision))
