# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
# Subject to Arista Networks, Inc.'s EULA.
# FOR INTERNAL USE ONLY. NOT FOR DISTRIBUTION.

from typing import List, Tuple
import tagsearch_python.tagsearch_pb2_grpc as tsgr
import tagsearch_python.tagsearch_pb2 as tspb

from cloudvision.cvlib import (
    ActionFailed,
    extractStudioInfoFromArgs,
    InputUpdateException,
    InputRequestException,
    setStudioInputs,
    getStudioInputs,
    IdAllocator,
)

# pylint: disable=undefined-variable

def tagSearchQuery(query, wrkID):
   devices = []
   tsclient = ctx.getApiClient(tsgr.TagSearchStub)
   tagmr = tspb.TagMatchRequestV2(
                      query=query,
                      workspace_id=wrkID,
                      topology_studio_request=True
                     )
   tagmresp = tsclient.GetTagMatchesV2(tagmr)
   for match in tagmresp.matches:
      if device_id := match.device.device_id:
         devices.append(device_id)
   return devices

inputSettings = []

def setInput(path: List, value: str):
   """
   Set the nodeId for the input path device in the inputs
   """
   inputSettings.append((path, value))

def sendInputSettings(stdID: str, wrkID: str, inputs: List[Tuple]):
   """
   Send the input settings to the Inputs Service
   """
   try:
      setStudioInputs(ctx.getApiClient, stdID, wrkID, inputs)
   except InputUpdateException as error:
      raise ActionFailed(("Failed to update inputs associated with switch Ids. "
                          "Please assign them manually.")) from error

class Selection:
   def __init__(self, site: int, group: int, stack: int):
      self.site = site
      self.group = group
      self.stack = stack

def getStackMemberPath(siteIdx, groupIdx, stackIdx):
   return ['sites', str(siteIdx), 'inputs', 'sitesGroup', 'devices',
            str(groupIdx), 'inputs', 'devicesGroup', 'stack',
            str(stackIdx), 'inputs', 'stackMember']

def getStackTagPath(siteIdx, groupIdx, stackIdx):
   return ['sites', str(siteIdx), 'inputs', 'sitesGroup', 'devices',
            str(groupIdx), 'inputs', 'devicesGroup', 'stack',
            str(stackIdx), 'tags', 'query']

def setStackMembers(inputs, wrkID, sel: Selection):
   allSites = inputs.get('sites')
   for siteIdx, site in enumerate(allSites):
      if not ( siteInputs := site.get( 'inputs' )) or not (
         siteTags := site.get( 'tags' ) ):
         continue
      if sel.site is not None and siteIdx != sel.site:
         continue
      siteDevs = tagSearchQuery(siteTags.get('query'), wrkID)
      siteGroups = siteInputs.get('sitesGroup', {}).get('devices')
      for groupIdx, siteGroup in enumerate(siteGroups):
         if not ( siteGroupInputs := siteGroup.get( 'inputs' )) or not (
           siteGroupTags := siteGroup.get( 'tags' ) ):
            continue
         if sel.group is not None and groupIdx != sel.group:
            continue
         groupDevs = tagSearchQuery(siteGroupTags.get('query'), wrkID)
         groupDevs = list(set(siteDevs) & set(groupDevs))
         stackEntries = siteGroupInputs.get('devicesGroup', {}).get('stack')
         stackDevs = []
         idAlloc = IdAllocator()
         # add existing Id's to allocator
         for stackIdx, stackEntry in enumerate(stackEntries):
            if not ( stackEntryQuery := stackEntry.get(
               'tags', {} ).get( 'query' ) ):
               continue
            if not (swid := stackEntry.get( 'inputs', {} ).get('stackMember')):
               continue
            devId = stackEntryQuery.split(':')[1]
            stackDevs.append(devId)
            idAlloc.allocate(int(swid), devId)
         # add mising Id's from allocator
         for stackIdx, stackEntry in enumerate(stackEntries):
            if not ( stackEntryQuery := stackEntry.get(
               'tags', {} ).get( 'query' ) ):
               continue
            if sel.stack is not None and stackIdx != sel.stack:
               continue
            if (swid := stackEntry.get( 'inputs', {} ).get('stackMember')):
               continue
            devId = stackEntryQuery.split(':')[1]
            stackDevs.append(devId)
            # allocate an swid
            swid = idAlloc.allocate(name=devId)
            path = getStackMemberPath(siteIdx, groupIdx, stackIdx)
            setInput(path, str(swid))
            if sel.stack is not None:
               return
         # add missing entries, and allocate them an id
         if len(stackDevs) < len(groupDevs):
            for stackIdx, devId in enumerate(groupDevs, start=len(stackDevs)):
               if devId in stackDevs:
                  continue
               # allocate an swid
               swid = idAlloc.allocate(name=devId)
               path_tags = getStackTagPath(siteIdx, groupIdx, stackIdx)
               setInput(path_tags, f"device:{devId}")
               path_input = getStackMemberPath(siteIdx, groupIdx, stackIdx)
               setInput(path_input, str(swid))

def main():
   stdID, wrkID, input_path = extractStudioInfoFromArgs(ctx.action.args)
   try:
      inputs = getStudioInputs(ctx.getApiClient, stdID, wrkID)
   except InputRequestException as error:
      raise ActionFailed((f"Failed to get input associated with {stdID}.")) from error
   site_index = None
   group_index = None
   stack_index = None
   if input_path.count('inputs') >= 1:
      site_index = int(input_path[input_path.index('sites')+1])
   if input_path.count('inputs') >= 2:
      group_index = int(input_path[input_path.index('devices')+1])
   if input_path.count('inputs') >= 3:
      stack_index = int(input_path[input_path.index('stack')+1])
   selection = Selection(site_index, group_index, stack_index)
   setStackMembers(inputs, wrkID, selection)
   if inputSettings:
      sendInputSettings(stdID, wrkID, inputSettings)

if __name__ == "__main__":
   main()
