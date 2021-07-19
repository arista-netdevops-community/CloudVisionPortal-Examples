#SNMP Localized Users Configlet Builder

**Objective**

This Configlet Builder amends a target configlet with a set of SNMP v3 User configurations that have been localized with the SNMP Engine ID for each device .
The script Generates a key from a passphrase as describe in RFC 2574 section A.2 and Performs the key localization as described in RFC 2574 section 2.6
The output generated appears like 

```
snmp-server user <user> <snmpGroup> v3 localized <engineID> auth <authType> <authKey> priv <privType> <privacyKey>
```

**Dependencies**

The script has dependencies on the following python libraries:
 - cvplibrary
 - json
 - os
 - re
 - ssl
 - hashlib

**Menu Options**

Select if running in Provisioning Hierarchy or Automatic update - default Hierarchy {{automatic}}
If automatic is selected then all provisioned switches in the CloudVision inventory that are not in the "Undefined" container
will have their interfaces checked and updated.
If automatic is not selected then the target device will be selected either through the provisioning process or from the "Device" drop down if 
the script is being used in the configlet edit mode

SNMP User Name(s) {{user_name,user_name}}
Enter a list of SNMP users names to work on, each name separated by a comma

Add or Replace Names {{add / replace}}
Add new names to existing SNMP names or replace all current names

SNMP Group Name(s) {{group_name,group_name}}
Enter a list of SNMP Groups separated by comas in the same order as the SNMP Users Names

User authentication values {{md5,sha,,sha224,sha256,sha384,sha512}}
Select One authentication Type from the list to apply to all users

Authentication Pass Phrase(s) {{snmpAuth1,snmpAuth2}}
Enter a list of Authentication Pass Phrases separated by comas in the same order as SNMP Users Names

Privacy Parameters {{des,aes,aes192,aes256}}
Select one Privacy algorithm for all users

Privacy Pass Phrase(s) {{snmpPriv1,snmpPriv2}}
Enter a list of Privacy Pass Phrases separated by comas in the same order as SNMP Users Names