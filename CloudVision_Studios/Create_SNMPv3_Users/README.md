# SNMPv3 Users
## Summary
The SNMPv3 Users Studio configures Localized SNMPv3 users where the localization is achieved by the use of a generated Engine ID.

> Note: In its beta-version, this studio does not currently support the configuration of the SNMPv3 Engine ID using the System MAC address of the switch as EOS does. This limitation is due to the current version of Studios (Beta) not being able to collect the system MAC address for the target switch. This limitation will be addressed in future Studios releases. This Studio will look for the System MAC but if it cannot be found it will use the last 6 digits of the switch serial number plus some padding to generate a unique Engine ID that remains consistent for the target switch.

The Studio will allow for the creation of SNMPv3 User profiles and their assignment to individual or groups of switches.