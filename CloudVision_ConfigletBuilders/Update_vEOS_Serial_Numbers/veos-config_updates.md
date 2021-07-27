#vEOS MAC address and Serial Number updater

**Objective**

These Configlet Builders amend the /mnt/flash/veos-config file on vEOS device to fix the system MAC address and serial number so that it remains constant over reloads.

**Dependencies**

The script has dependencies on the following python libraries:
 - cvplibrary
 - json
 - os
 - re

**Menu Options**

Select if running in Provisioning Hierarchy or Automatic update - default Hierarchy {{automatic}}
If automatic is selected then all provisioned switches in the CloudVision inventory that are not in the "Undefined" container
will have their interfaces checked and updated.
If automatic is not selected then the target device will be selected either through the provisioning process or from the "Device" drop down if the script is being used in the configlet edit mode
