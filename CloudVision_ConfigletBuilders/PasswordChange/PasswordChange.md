#PasswordChange

**Objective**

This Configlet Builder allows the user to change and encrypt passwords inside a Configlet. The Builder was originally developed to assist Operational teams change the local user password for admin and cvpadmin on their switches using CVP. The builder menu has the option to add two additional users into the Configlets and define custom user roles. The builder also uses the menu item dependency option to only reveal menu fields that are required for specific users.

**Dependencies**

The script has dependencies on the following python libraries:
 - cvplibrary
 - re
 - subprocess
