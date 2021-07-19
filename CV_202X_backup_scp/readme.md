# Backup and Copy

## Objective

This script expands the capabilities of the backup.py script provided with CloudVision Portal and adds the ability to copy the files created during the backup to a remote host.

## Dependencies

The script has been written to use the libraries provided with CloudVision so does not require any additional libraries when run on CloudVision Portal.
Outside of CloudVision the script requires:

- argparse
- subprocess
- pexpect
- cryptography
- iniparse
- glob
- os
- pprint
- sys
- datetime

## Command Line Options

The script has the following command line options to complete:

- limit {{NumBackups}}  -  Number of Backup files to keep on CloudVision in
                        /data/cvpbackup/
                        The option will be overridden by the settings in
                        the .ini file and defaults to 5 if not set.

- ini {{ini File Path}} -  full file path to .ini file containing remote
                        host details and backup limits (see later).
                        Defaults to ./backup.ini if not specified.

## INI file Options

The .ini file for this script provides the following options:

- user = {{username}}  -   User name to access the remote host with and SCP
                        backup files with. The User must have write permissions to the destination directory.

- server = {{IP/URL}}  -   Remote host IP address of URL

- password = {{password}} - encrypted form of user password.
                        This can be generated using the iniEditor.py
                        script provided. (See later)

- keyFile = {{file path}} - full path and file name for the file containing
                        the decryption key for the password provided

- destination = {{file path}} -  full path to directory on remote host for
                              backup files to be copied to. Does not require host details.
                              Example \backups\cvp\

- limit = {{Number Backups}}  -   Number of backup files of each type to keep


### INI file Example:

[Server_Settings]

#Backup Server Settings

user = {{user name to access remote host}}

server = {{URL or IP of remote host}}

password = {{encrypted password for user}}

keyFile = {{full path to location of encryption key}}

destination = {{full path to destination directory on remote host}}

[Backup_Settings]

#Backup script settings

limit = {{number of backups to keep}}

## iniEditor

### Dependencies

The script has been written to use the libraries provided with CloudVision so does not require any additional libraries when run on CloudVision Portal.
Outside of CloudVision the script requires:

- cryptography
- argparse
- iniparse
- sys
- os

### Command Line Options

The script has the following command line options to complete:

- ini {{file path}}  -  full file path and filename for the backup Settings
                     .ini file described above.
                     Defaults to ./backup.ini

## newKeyGen

### Dependencies

The script has been written to use the libraries provided with CloudVision so does not require any additional libraries when run on CloudVision Portal.
Outside of CloudVision the script requires:

- cryptography
- argparse
- iniparse

### Command Line Options

The script has the following command line options to complete:

- ini {{file path}}  -  full file path and filename for the backup Settings
                     .ini file described above.
                     Defaults to ./backup.ini

## Script Usage

### backupCopy

The backup script can be executed either on the command line or in the crontab. The command option is executed as follows:

/home/cvpadmin/backupCopy.py --ini /home/cvpadmin/backup.ini

This will execute the script which in turn will attempt to complete a backup of CloudVision Portal. Once the backup is complete the script will then attempt to copy any backup files created during the backup. Normally this will be the backup log file (e.g. backup_cvp.20210715020003.log) and the CVP backup (e.g. cvp.20210715101112.tgz). If the Image Bundles in CloudVision have recently been updated then an additional EOS Images file may be created (e.g. cvp.eosimages.20210710020003.tgz) this will also be copied to the remote host.

To use the backupCopy script with crontab:

The current backup script is executed using cron. It is currently set to run everyday at 02:00am and a logbackup is scheduled to run at 03:00am every Friday.

```
# crontab -l
0 2 * * * /cvpi/tools/backup.py --limit 5
0 3 * * 5 /cvpi/tools/logsbackup.py --limit 5
```
To schedule cronjobs to perform the periodic backups use the following command:
```
# crontab -e
0 2 * * * /cvpi/tools/backup.py --limit 5
0 3 * * 5 /cvpi/tools/logsbackup.py --limit 5
```
the crontab can then be edited as shown below
```
# crontab -e
0 2 * * * /home/cvpadmin/backupCopy.py --ini /home/cvpadmin/backup.ini
0 3 * * 5 /cvpi/tools/logsbackup.py --limit 5
```
the following commands will save the edits made:
```
esc
:wq <cr>
```
For more details on the use of crontab the following website is very useful:
		http://www.nncron.ru/help/EN/working/cron-format.htm

It is important to ensure that the script is marked as executable and owned by cvp otherwise it will not work in cron.

A successful execution of the script will result in the creation of a backup in CVP and the related backup file being copied to the remote host.

### iniEditor

The iniEditor makes editing the backup.ini file a simpler task. The script will review the contents of the ini file and provide the option to edit them. An example workflow is shown below:
```
# ./iniEditor.py --ini ./backup.ini
#####  Current Server Settings   #####

 destination : /data/cvpbackups/
 password : gAAAAABg7xoT7PVgqYI5c69wQyPeG-25O5__Ps_WoWO86zLUUvt2wKy22nxHHv15osJ5DXPl-WplAGkTPLpxRs-JNRrqpv7hjw==
 keyfile : key.key
 user : username
 server : 10.10.10.10

Would you like to edit these settings? (y/n) y
Change Value or hit Enter to use current

 destination : /data/cvpbackups/
 password : gAAAAABg7xoT7PVgqYI5c69wQyPeG-25O5__Ps_WoWO86zLUUvt2wKy22nxHHv15osJ5DXPl-WplAGkTPLpxRs-JNRrqpv7hjw==
   Change Password : gAAAAABg7xoT7PVgqYI5c69wQyPeG-25O5__Ps_WoWO86zLUUvt2wKy22nxHHv15osJ5DXPl-WplAGkTPLpxRs-JNRrqpv7hjw== (y/n) y
   Please enter current password: password
   Please enter new password password
   Password password changed to password
   Would you like to apply change? (y/n) y

  keyfile : key.key
   Update Key / Key File : key.key (y/n) y
   (A)ssign new key file or (U)pdate Key ?(a/u) a
   Please enter full path and filename for key file ./key.key
   Updating current Password using new Key File

 user : username
 server : 10.10.10.10


#####  New Server Settings   #####

 destination : /data/cvpbackups/
 password : gAAAAABg8BHRjwsKuUWInGcsGrGZ8ihwyKQfaQVXxRAgolfKQCGZZL9hcZIcRfWzbgD652S-GFI73GsBbBeP65PTaGkfyuKTAw==
 keyfile : ./key.key
 user : username
 server : 10.10.10.10


#####  Updating ./backup.ini   #####
```

### newKeyGen

The newKeyGen takes the ini file specified in the command line and overwrites the key file information with a new key file that it generates. It then amends the password setting by overwriting it with a new encrypted password based on the entered clear text password and newly generated key. The actions in this script are not reversible any existing passwords will be lost.
