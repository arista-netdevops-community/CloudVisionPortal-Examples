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
import json
import yaml
from pyavd._cv.api.arista.studio.v1 import (
    Inputs,
    InputsKey,
    InputsServiceStub,
    InputsStreamRequest,
)
import argparse
import logging

from pyavd._cv.client import CVClient

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

async def backup_studios(cloudvision: CloudVision):
    async with CloudVision as cv_client:
        result = await get_studio_inputs_all(cv_client)
        for studio in result:
            # filter out SCS inputs
            if studio['studio_id'] == "studio-static-configlet":
                continue
            with open(f"{studio['studio_id']}.yaml", "w") as f:
                yaml.dump(studio['inputs'], f)

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

    args = parser.parse_args()

    # setup logging level from args and do initial debug logging
    logging.basicConfig(level=args.log_level)
    logging.info("Script starting")
    logging.debug("Arguments parsed")
    logging.debug(args)

    token = args.token_file.read().strip()
    CloudVision = CVClient(servers=args.apiserver_url,token=token, verify_certs=False)
    asyncio.run(backup_studios(CloudVision))
