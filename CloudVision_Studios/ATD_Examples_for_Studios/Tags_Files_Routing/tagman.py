#! /usr/bin/env python
# Copyright (c) 2022 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.
#
# Version 0.5
#
# This script is idempotent, ie. there is no harm in running multiple times.
#
# It must be run from the console of one of the cvp nodes
#
# Example usages:
#  ./tagman.py -u cvpadmin -p arastra -c localhost -f tagsfile.txt
#  ./tagman.py -u cvpadmin -p arastra -c localhost -f tagsfile.txt -d serialNumber
#  ./tagman.py -u cvpadmin -p arastra -c localhost -f tagsfile.txt -o delete 
#  ./tagman.py -u cvpadmin -p arastra -c localhost -f tagsfile.txt -a export
#  ./tagman.py -u cvpadmin -p arastra -c localhost -f tagsfile.txt -a export -d serialNumber 
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
import json
from json import JSONDecoder
import requests
import re
import subprocess
import urllib3

def json_decoder(data):
   decoder = JSONDecoder()
   pos = 0
   result = []
   while True:
      try:
         o, pos = decoder.raw_decode(data, pos)
         result.append(o)
         pos +=1
      except:
         break
   return result

def parseArgs():
   parser = argparse.ArgumentParser()
   parser.add_argument( '-c', '--cvpName', required=True, help='cvp name' )
   parser.add_argument( '-u', '--userId', required=True, help='username' )
   parser.add_argument( '-p', '--password', required=True, help='password' )
   parser.add_argument( '-f', '--filename', required=True,
				   help='single tag assignment per line: label, value, device' )
   parser.add_argument( '-o', '--operation', choices=['add', 'delete'], default='add',
				   help='add or delete' )
   parser.add_argument( '-a', '--action', choices=['import', 'export'], default='import',
				   help='import or export' )
   parser.add_argument( '-d', '--deviceIdentifier', choices=['hostname', 'serialNumber'],
				   default='hostname', help='deviceId in file is serialNumber or hostname' )
   args = vars( parser.parse_args() )
   return args.pop( 'cvpName' ), args.pop( 'filename'), args.pop( 'operation' ), args.pop( 'action' ), args.pop( 'deviceIdentifier'), args

def getCvpInfo( cvpName ):
   api = 'cvpInfo/getCvpInfo.do'
   url = 'https://%s:443/web/%s' % ( cvpName, api ) 
   return requests.get( url, cookies=cookies, verify=False )

def authenticate( cvpName, loginInfo ):
   url = 'https://%s:443/web/login/authenticate.do' % ( cvpName, )
   return requests.post( url, json.dumps( loginInfo ), verify=False )

# read tags from a text file:
def readTextFileToList(filename, tags, tagAssigns):
   with open(filename) as f:
      for line in f:
         aline = line.split(',')
         if line[0] == '#' or len(aline) != 3:
            continue
         tags[(aline[0].strip(), aline[1].strip())] = True
         if deviceIdentifier == 'hostname':
            deviceID = host2Id[aline[2].strip()]
         else:
            deviceID = aline[2].strip()
         tagAssigns.append((aline[0].strip(), aline[1].strip(), deviceID))

# write tags to a text file:
def writeListToTextFile(filename, tagAssigns):
   with open(filename, 'w') as f:
      f.write("# User tags exported from %s\n" % cvpName)
      f.write("# CVP version %s\n" % getCvpInfo( cvpName).json()["version"])
      f.write("# Date generated: %s\n" % datetime.datetime.now())
      for entry in tagAssigns:
         (tagLabel, tagValue, deviceId) = entry
         if deviceIdentifier == 'hostname':
            device = id2Host.get(deviceId)
            if not device:
              continue
         else:
            device = deviceId
         f.write("%s, %s, %s\n" % (tagLabel, tagValue, device))

def get_all_devices():
   device_url = '/api/resources/inventory/v1/Device/all'
   url = cvp_url + device_url
   response = requests.get(url, cookies=cookies, verify=False)
   device_data = json_decoder(response.text)
   host2Id = {}
   id2Host = {}
   for device in device_data:
      host2Id[device['result']['value']['hostname']] = device['result']['value']['key']['deviceId']
      id2Host[device['result']['value']['key']['deviceId']] = device['result']['value']['hostname']
   return host2Id, id2Host

def get_all_device_tags():
   tag_url = '/api/resources/tag/v1/DeviceTag/all'
   url = cvp_url + tag_url
   response = requests.get(url, cookies=cookies, verify=False)
   tag_data = json_decoder(response.text)
   tags = {}
   for tag in tag_data:
      tags[(tag['result']['value']['key']['label'],tag['result']['value']['key']['value'])] = tag['result']['value']['creatorType']
   return tags

def get_all_device_tag_assignments():
   tag_url = '/api/resources/tag/v1/DeviceTagAssignmentConfig/all'
   url = cvp_url + tag_url
   response = requests.get(url, cookies=cookies, verify=False)
   tag_assigns_data = json_decoder(response.text)
   tag_assigns = {} 
   for tag_assign in tag_assigns_data:
      tag_assigns.setdefault((tag_assign['result']['value']['key']['label'],tag_assign['result']['value']['key']['value']), []).append(tag_assign['result']['value']['key']['deviceId'])
   return tag_assigns

def create_dtag(label, value):
   tag_url = '/api/resources/tag/v1/DeviceTagConfig'
   payload = {"key":{"label":label, "value":value}}
   url = cvp_url + tag_url
   response = requests.post(url, cookies=cookies, data=json.dumps(payload), verify=False)
   return response

def delete_dtag(label, value):
   tag_url = '/api/resources/tag/v1/DeviceTagConfig?key.label=%s&key.value=%s' % (label, value)
   url = cvp_url + tag_url
   response = requests.delete(url, cookies=cookies, verify=False)
   return response

def unassign_dtag(dId, label, value):
   tag_url = '/api/resources/tag/v1/DeviceTagAssignmentConfig?key.label=%s&key.value=%s&key.device_id=%s' % (label, value, dId)
   url = cvp_url + tag_url
   response = requests.delete(url, cookies=cookies, verify=False)
   return response

def assign_dtag(dId, label, value):
   tag_url = '/api/resources/tag/v1/DeviceTagAssignmentConfig'
   payload = {"key":{"label":label, "value":value, "deviceId": dId}}
   url = cvp_url + tag_url
   response = requests.post(url, cookies=cookies, data=json.dumps(payload), verify=False)
   return response

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

   if operation == "add":
      print("Adding Tags:")
      for tag in sorted(tagList):
         print("  {}:{}".format(tag[0],tag[1]))
         create_dtag(tag[0], tag[1])
      print("Assigning Tags:")
      for tagAssign in tagAssignList:
         print("  {}:{} - {}".format(tagAssign[0], tagAssign[1], tagAssign[2]))
         assign_dtag(tagAssign[2], tagAssign[0], tagAssign[1])
   elif operation == "delete":
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
      if tags.get(key) and tags[key] == 'CREATOR_TYPE_USER':
         (taglabel, tagvalue) = key
         for device in devices:
            tagAssignList.append((taglabel, tagvalue, device))
   writeListToTextFile(filename, tagAssignList)

if __name__ == '__main__':
   urllib3.disable_warnings()
   cvpName, filename, operation, action, deviceIdentifier, loginInfo  = parseArgs() 
   cvp_url = 'https://%s' % cvpName
   cookies = authenticate( cvpName, loginInfo ).cookies
   print(json.dumps(getCvpInfo( cvpName ).json(), indent=2))
   host2Id, id2Host = get_all_devices()
   if action == 'import':
      importTags(filename)
   elif action == 'export':
      exportTags(filename)
