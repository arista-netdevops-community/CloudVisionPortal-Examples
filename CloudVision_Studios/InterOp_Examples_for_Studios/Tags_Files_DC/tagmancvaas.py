#! /usr/bin/env python
# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Version 0.7
#
# This script is idempotent, ie. there is no harm in running multiple times.
#
# For instructions on getting the token and cert-files refer to:
#  https://github.com/aristanetworks/cloudvision-python/tree/trunk/examples/resources/inventory
#
# Example usages for on-prem cvp:
#  python3 tagman.py -tk token.txt -cf cvp.crt -c cvp1000 -f tagsfile.txt
#  python3 tagman.py -tk token.txt -cf cvp.crt -c cvp1000 -f tagsfile.txt -d serialNumber
#  python3 tagman.py -tk token.txt -cf cvp.crt -c cvp1000 -f tagsfile.txt -o delete 
#  python3 tagman.py -tk token.txt -cf cvp.crt -c cvp1000 -f tagsfile.txt -a export
#  python3 tagman.py -tk token.txt -cf cvp.crt -c cvp1000 -f tagsfile.txt -a export -d serialNumber 
#
# Example usages for cvaas:
#  python3 tagman.py -tk cvaasToken.txt -c www.arista.io:443 -f tagsfile.txt
#  ... etc as in on-prem examples
#
# Example file tagsfile.txt:
#     # This is a file of L3LS Studio Tags
#     # one line per tag assignment
#     # comma separated label, value ,device
#     # file can have comments like this which are ignored
#     DC, DC1, do454
#     DC, DC1, gd375
#     DC-POD, POD1, do454
#     DC-POD, POD1, gd375
#     # ignore this line DC-POD, POD2, gd375
#     Role, Spine, do454
#     Role, Leaf, gd375
#     Spine-Number, 1, do454
#     Leaf-Number, 1, gd375

import argparse
import datetime
import re
import subprocess

import grpc

# import the tags models and services
from arista.tag.v1 import models as tagModels
from arista.tag.v1 import services as tagServices
# import the inventory models and services
from arista.inventory.v1 import models as invModels
from arista.inventory.v1 import services as invServices

from google.protobuf import wrappers_pb2 as wrappers

RPC_TIMEOUT = 30  # in seconds

def parseArgs():
   parser = argparse.ArgumentParser()
   parser.add_argument( '-c', '--cvpName', required=True, help='cvp name' )
   parser.add_argument( '-f', '--filename', required=True,
				   help='single tag assignment per line: label, value, device' )
   parser.add_argument( '-o', '--operation', choices=['add', 'delete'], default='add',
				   help='add or delete' )
   parser.add_argument( '-a', '--action', choices=['import', 'export'], default='import',
				   help='import or export' )
   parser.add_argument( '-d', '--deviceIdentifier', choices=['hostname', 'serialNumber'],
				   default='hostname', help='deviceId in file is serialNumber or hostname' )
   parser.add_argument( '-tk', '--token-file', required=True,
                        type=argparse.FileType('r'), help="file with access token" )
   parser.add_argument( '-cf', '--cert-file', type=argparse.FileType('rb'),
                        help="certificate to use as root CA" )
   args = parser.parse_args()
   return args

# read tags from a text file:
def readTextFileToList(filename, tags, tagAssigns):
   with open(filename) as f:
      for line in f:
         aline = line.split(',')
         if line[0] == '#' or len(aline) != 3:
            continue
         tags[(aline[0].strip(), aline[1].strip())] = True
         if args.deviceIdentifier == 'hostname':
            deviceID = host2Id.get(aline[2].strip())
            if deviceID == None:
               # skip assignment for device not in inventory 
               print("skipping tag {}:{} for device {} not in inventory".format(
                  aline[0].strip(), aline[1].strip(), aline[2].strip()))
               continue
         else:
            deviceID = aline[2].strip()
         tagAssigns.append((aline[0].strip(), aline[1].strip(), deviceID))

# write tags to a text file:
def writeListToTextFile(filename, tagAssigns):
   with open(filename, 'w') as f:
      f.write("# User tags exported from %s\n" % args.cvpName)
      f.write("# Date generated: %s\n" % datetime.datetime.now())
      for entry in tagAssigns:
         (tagLabel, tagValue, deviceId) = entry
         if args.deviceIdentifier == 'hostname':
            device = id2Host.get(deviceId)
            if device == None:
               # skip assignment for device not in inventory 
               print("skipping tag {}:{} for device {} not in inventory".format(
                  tagLabel, tagValue, deviceId))
               continue
         else:
            device = deviceId
         f.write("%s, %s, %s\n" % (tagLabel, tagValue, device))

def get_all_devices():
    host2Id = {}
    id2Host = {}
    get_all_req = invServices.DeviceStreamRequest()
    inv_filter = invModels.Device()
    get_all_req.partial_eq_filter.append(inv_filter)
    # initialize a connection to the cvp using our connection settings (auth + TLS)
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        inv_stub = invServices.DeviceServiceStub(channel)
        for resp in inv_stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
            host2Id[resp.value.hostname.value] = resp.value.key.device_id.value
            id2Host[resp.value.key.device_id.value] = resp.value.hostname.value 

    return host2Id, id2Host

def get_all_device_tags():
    tags = {}
    get_all_req = tagServices.DeviceTagStreamRequest()
    tag_filter = tagModels.DeviceTag()
    get_all_req.partial_eq_filter.append(tag_filter)
    # initialize a connection to the cvp using our connection settings (auth + TLS)
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagServiceStub(channel)
        for resp in tag_stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
            tags[(resp.value.key.label.value, resp.value.key.value.value)] = resp.value.creator_type
    return tags

def get_all_device_tag_assignments():
    tag_assigns = {}
    get_all_req = tagServices.DeviceTagAssignmentConfigStreamRequest()
    tag_filter = tagModels.DeviceTagAssignmentConfig()
    get_all_req.partial_eq_filter.append(tag_filter)
    # initialize a connection to the cvp using our connection settings (auth + TLS)
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagAssignmentConfigServiceStub(channel)
        for resp in tag_stub.GetAll(get_all_req, timeout=RPC_TIMEOUT):
            tag_assigns.setdefault((resp.value.key.label.value,resp.value.key.value.value), []).append(resp.value.key.device_id.value)
    return tag_assigns

def create_dtag(label, value):
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagConfigServiceStub(channel)

        req = tagServices.DeviceTagConfigSetRequest(
            value=tagModels.DeviceTagConfig(
                key=tagModels.TagKey(
                    label=wrappers.StringValue(value=label),
                    value=wrappers.StringValue(value=value)
                )
            )
        )
        try:
            tag_stub.Set(req, timeout=RPC_TIMEOUT)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
                pass
        except Exception as e:
            print('create_dtag of {}:{} - got error {}'.format(label, value, e))


def delete_dtag(label, value):
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagConfigServiceStub(channel)

        req = tagServices.DeviceTagConfigDeleteRequest(
            key=tagModels.TagKey(
                label=wrappers.StringValue(value=label),
                value=wrappers.StringValue(value=value)
            )
        )
        try:
            tag_stub.Delete(req, timeout=RPC_TIMEOUT)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                pass
        except Exception as e:
            print('delete_dtag of {}:{} - got error {}'.format(label, value, e))


def unassign_dtag(dId, label, value):
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagAssignmentConfigServiceStub(channel)

        req = tagServices.DeviceTagAssignmentConfigDeleteRequest(
            key=tagModels.DeviceTagAssignmentKey(
                label=wrappers.StringValue(value=label),
                value=wrappers.StringValue(value=value),
                device_id=wrappers.StringValue(value=dId)
            )
        )
        try:
            tag_stub.Delete(req, timeout=RPC_TIMEOUT)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                pass
        except Exception as e:
            print('unassign_dtag of {}:{} on {} - got error {}'.format(label, value, dId, e))

def assign_dtag(dId, label, value):
    with grpc.secure_channel(args.cvpName, connCreds) as channel:
        tag_stub = tagServices.DeviceTagAssignmentConfigServiceStub(channel)

        req = tagServices.DeviceTagAssignmentConfigSetRequest(
            value=tagModels.DeviceTagAssignmentConfig(
                key=tagModels.DeviceTagAssignmentKey(
                    label=wrappers.StringValue(value=label),
                    value=wrappers.StringValue(value=value),
                    device_id=wrappers.StringValue(value=dId)
                )
            )
        )
        try:
            tag_stub.Set(req, timeout=RPC_TIMEOUT)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
                pass
        except Exception as e:
            print('assign_dtag of {}:{} on {} - got error {}'.format(label, value, dId, e))


def get_devices_from_tag_path(label, value):
   cmd = '/cvpi/tools/apish get --dataset-name analytics --path "/tags/labels/devices/%s/value/%s/elements" --pretty' % (label, value)
   p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   devices = []
   for line in p.stdout.readlines():
      if 'deviceID' in line:
          p = re.compile('"deviceID":(.*)')
          device = p.findall(line)[0].strip().strip('\"')
          devices.append(device)
   return devices

def importTags(filename):
   tagList = {}
   tagAssignList = []
   readTextFileToList(filename, tagList, tagAssignList)

   if args.operation == "add":
      print("Adding Tags:")
      for tag in sorted(tagList):
         print("  {}:{}".format(tag[0],tag[1]))
         create_dtag(tag[0], tag[1])
      print("Assigning Tags:")
      for tagAssign in tagAssignList:
         print("  {}:{} - {}".format(tagAssign[0], tagAssign[1], tagAssign[2]))
         assign_dtag(tagAssign[2], tagAssign[0], tagAssign[1])
   elif args.operation == "delete":
      print("Unassigning Tags:")
      for tagAssign in tagAssignList:
         print("  {}:{} - {}".format(tagAssign[0], tagAssign[1], tagAssign[2]))
         unassign_dtag(tagAssign[2], tagAssign[0], tagAssign[1])
      print("Deleting Tags:")
      for tag in sorted(tagList):
         print("  {}:{}".format(tag[0],tag[1]))
         delete_dtag(tag[0], tag[1])

def exportTags(filename):
   tagAssignList = []
   tags = get_all_device_tags()
   for key, devices in get_all_device_tag_assignments().items():
      if tags.get(key) and tags[key] == tagModels.CREATOR_TYPE_USER:
         (taglabel, tagvalue) = key
         for device in devices:
            tagAssignList.append((taglabel, tagvalue, device))
   writeListToTextFile(filename, tagAssignList)

if __name__ == '__main__':
    args = parseArgs()
    # read the file containing a session token to authenticate with
    token = args.token_file.read().strip()
    # create the header object for the token
    callCreds = grpc.access_token_call_credentials(token)

    # if using a self-signed certificate (should be provided as arg)
    if args.cert_file:
        # create the channel using the self-signed cert
        cert = args.cert_file.read()
        channelCreds = grpc.ssl_channel_credentials(root_certificates=cert)
    else:
        # otherwise default to checking against CAs
        channelCreds = grpc.ssl_channel_credentials()
    connCreds = grpc.composite_channel_credentials(channelCreds, callCreds)

    host2Id, id2Host = get_all_devices()
    if args.action == 'import':
        importTags(args.filename)
    elif args.action == 'export':
        exportTags(args.filename)
