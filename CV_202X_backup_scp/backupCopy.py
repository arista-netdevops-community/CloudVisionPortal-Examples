#! /usr/bin/env python
#
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
#
# Tool to create backup of CVP.
# Modified to SCP or SFTP files off box

import argparse
from subprocess import call
import pexpect
from cryptography.fernet import Fernet
import iniparse
import glob
import os
from pprint import pprint
import sys
import datetime

def log(message,maxSize=1000):
    destDir = str(os.path.abspath(os.path.dirname(sys.argv[0])))
    logFile = destDir+"/backupCopy.log"
    if os.path.exists(logFile) and os.path.getsize(logFile) < maxSize:
        with open(logFile, 'a') as fp:
                fp.writelines(message)
    else:
        with open(logFile, 'w') as fp:
                fp.writelines(message)

def backupLists():
    ''' Get the current backup lists'''
    backupList = glob.glob("/data/cvpbackup/*")
    backupDataList = []
    backupImageList = []
    for b in backupList:
        if 'eosimages' in b:
            backupImageList.append(b)
        elif 'tgz' in b:
            backupDataList.append(b)
    backupLogList = glob.glob( "/cvpi/logs/cvpbackup/backup_cvp.*.log" )
    return [sorted(backupDataList), sorted(backupImageList), sorted(backupLogList)]

def fileFromPath(filepath):
    '''Split Full file path into directory list
        return the last entry in list as this is
        the file name'''
    return filepath.split('/')[-1]

def getBackupFiles():
    """Extract latest backup files from backup list output"""
    backupDataList, backupImageList, backupLogList = backupLists()
    fileList = [[backupDataList[-1], fileFromPath(backupDataList[-1])],
                [backupImageList[-1], fileFromPath(backupImageList[-1])],
                [backupLogList[-1], fileFromPath(backupLogList[-1])]]
    return fileList

def createBackup( limit):
   '''Create one-shot backup of CVP.
   Arguments:
      limit  -- The threshold value after which the oldest backup will be
                removed if a new backup creation is initiated.
   '''
   ret = False
   try:
      # Get the current backup lists
      backupDataList, backupImageList, backupLogList = backupLists()
      print ('Starting Backup Data List:')
      pprint(backupDataList)
      print ('Starting Backup Image List:')
      pprint(backupImageList)
      print ('Starting Backup Log List:')
      pprint(backupLogList)
      log("Strarting Backup Lists:\n%s\n%s\n%s\n"%(backupDataList, backupImageList, backupLogList))

      # Determine the starting oldest key
      now = datetime.datetime.now()
      oldestDataKey = now.strftime("%Y%m%d%H%M%S")
      lenBackupDataList = len( backupDataList )
      if lenBackupDataList > 0:
         oldestDataKey = filter(str.isdigit, backupDataList[ 0 ])

      # Limit the number of pre-existing data backups
      if limit and lenBackupDataList >= limit:
        print( 'Found %d backup files more than the configured limit\n'
                 % ( lenBackupDataList - limit + 1 ))
        log( 'Found %d backup files more than the configured limit\n'
                % ( lenBackupDataList - limit + 1 ))
        # Reduce no. of backups stored to limit-1
        for i in range( 0, lenBackupDataList - limit + 1 ):
            print( '   %d: Deleting old backup data file: %s\n'
                % ( i, backupDataList[ 0 ] ))
            log( '   %d: Deleting old backup data file: %s\n'
                % ( i, backupDataList[ 0 ] ))
            os.remove(backupDataList[ 0 ])
            oldestDataKey = filter(str.isdigit, backupDataList[ 0 ])
            backupDataList.pop(0)

      # Leave only one image backup as old as the oldest remaining data backup
      if len(backupDataList) > 0:
        oldestDataKey = filter(str.isdigit, backupDataList[ 0 ])
        savedOne = False
      for imgfile in reversed(backupImageList):
        imageKey = filter(str.isdigit, imgfile)
        if imageKey <= oldestDataKey and savedOne == False:
            savedOne = True
        elif imageKey <= oldestDataKey:
            print('   Deleting old backup image file: %s\n'%imgfile)
            log('   Deleting old backup image file: %s\n'%imgfile)
            os.remove(imgfile)
            backupImageList.remove(imgfile)

      # Remove backup logfiles older than oldest remaining data backup
      for logfile in reversed(backupLogList):
        logKey = filter(str.isdigit, logfile)
        if logKey < oldestDataKey:
            print('   Deleting old backup log file: %s\n' %logfile)
            log('   Deleting old backup log file: %s\n' %logfile)
            os.remove(logfile)
            backupLogList.remove(logfile)

      print('Ending Backup Data List:')
      pprint(backupDataList)
      print ('Ending Backup Image List:')
      pprint(backupImageList)
      print ('Ending Backup Log List:')
      pprint(backupLogList)
      log("End Backup Lists:\n%s\n%s\n%s\n"%(backupDataList, backupImageList, backupLogList))

      # Create backup
      print('Creating a new backup. This may take some time...\n')
      log('Creating a new backup. This may take some time...\n')
      ret = call('su - cvp -c "cvpi backup cvp"', shell=True)
      print('Backup created\n')
      log('Backup created\n')
   except OSError as e:
       print('Error Creating backup: %s\n'%e)
       log('Error Creating backup: %s\n'%e)
       ret = True
   return ret

def scpFile( srcFile, destFile, server, user, password):
    '''SCP Files created during backup to remote server.
    Arguments:
        srcFile   --  full file path to the local file to be copied
                    e.g. /data/cvpbackup/cvp.20210713201558.tgz
        destFile  --  full file path for the remote file location
                    e.g. /backups/cvp.20210713201558.tgz
        server    --  IP address or URL for remote host
        user      --  Username with access to required file path
                    on remote host
        password  --  Password for above user
    '''
    # Define response strings to match
    SSH_NEWKEY = r'Are you sure you want to continue connecting \(yes/no\)\?'
    SSH_PSSWD = r'[Pp]assword: '
    # Create SCP command to use in shell
    cmd = "scp "+srcFile+" "+user+"@"+server+":"+destFile
    # Create Expext object and execute command
    response = pexpect.spawn(cmd)
    options = response.expect([pexpect.TIMEOUT, SSH_NEWKEY, SSH_PSSWD])
    if options == 0: # Command Timed Out
        print('SCP ERROR - SSH Timedout:\n   %s\n   %s\n' %(response.before, response.after))
        log('SCP ERROR - SSH Timedout:\n   %s\n   %s\n' %(response.before, response.after))
        return False
    elif options == 1:  # SSH does not have the public key. Just accept it.
        response.sendline('yes')
        response.expect(SSH_PSSWD)
        response.sendline(password)
    elif options == 2: # SSH requires a password
        response.sendline(password)
    else: # One of the expect options was not matched
        print('SCP ERROR - SSH could not login:\n   %s\n   %s\n' %(response.before, response.after))
        log('SCP ERROR - SSH could not login:\n   %s\n   %s\n' %(response.before, response.after))
        return False
    options = response.expect(['Permission denied', '100%', 'Failed to open', 'No such'])
    if options == 0: # Remote Host has denied the file copy or login
        print('SCP ERROR - Username/Password or File Permissions Wrong:\n   %s\n   %s\n' %(response.before, response.after))
        log('SCP ERROR - Username/Password or File Permissions Wrong:\n   %s\n   %s\n' %(response.before, response.after))
        return False
    elif options == 1: # File was successfully copied to remote host
        print('Copied: %s\n' %response.after)
        log('Copied: %s\n' %response.after)
        return True
    elif options == 2: # File permissions problem
        print('SCP ERROR - User does not have write permission to file or directory:\%s\n' %destFile)
        log('SCP ERROR - User does not have write permission to file or directory:\%s\n' %destFile)
        return False
    elif options == 3: # File access problem
        print('SCP ERROR - Directory does not exist:\%s\n' %destFile)
        log('SCP ERROR - Directory does not exist:\%s\n' %destFile)
        return False
    else:
        print('SCP ERROR:\n   %s\n   %s\n' % (response.before, response.after)) # Something else went wrong
        log('SCP ERROR:\n   %s\n   %s\n' % (response.before, response.after)) # Something else went wrong
        return False

def parseArgs():
    parser = argparse.ArgumentParser( description='CVP backup tool' )
    parser.add_argument( '--limit', default=5, help='Limit the number of backups to'
                        ' the specified value (INI file setting will override)', type=int, choices=range( 1, 30 ) )
    parser.add_argument('--ini', default='./backup.ini', help='Ini file location, default to ./')
    args = parser.parse_args()
    return args

def main():
    options = parseArgs()
    # fetch the script options from the ini file
    iniFile = iniparse.ConfigParser()
    iniFile.read(options.ini)

    # Get Server optins from ini
    server = iniFile.get("Server_Settings","server")
    user = iniFile.get("Server_Settings","user")
    destination = iniFile.get("Server_Settings", "destination")

    # Decrypt Passed word using key value in script
    key = open(iniFile.get("Server_Settings", "keyFile"),"rb").read()
    f = Fernet(key)
    password = f.decrypt(iniFile.get("Server_Settings", "password"))

    # Set max number of backups to keep
    if iniFile.has_section("Backup_Settings"):
        limit = int(iniFile.get("Backup_Settings","limit"))
        log('Backup Limit set to: %s from INI file\n' %limit)
    else:
        limit = options.limit
        log('Backup Limit set to: %s from Args/default\n' %limit)

    # Make a note of time of day just before back starts
    nowKey = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    print("Backup Started: %s\n"%nowKey)
    log("Backup Started: %s\n"%nowKey)

    ret = createBackup( limit )
    # Get list of files created during backup
    # Prevents older EOS-Image files from being copied
    fileList = getBackupFiles()

    # Compare file keys and only copy more recent files
    scpdFiles = []
    for path,entry in fileList:
        if filter(str.isdigit, entry) >= nowKey:
            dest = destination+entry
            print("Copying %s to %s %s\n" %(entry, server, dest))
            log("Copying %s to %s %s\n" %(entry, server, dest))
            if scpFile(path, dest, server, user, password):
                scpdFiles.append(entry)
    print('Backup Files copied')
    pprint(scpdFiles)
    log("Backup Files copied:\n %s\n"%scpdFiles)
    nowKey = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    print("Backup Finished: %s\n"%nowKey)
    log("Backup Finished: %s\n"%nowKey)
    return int( ret )

if __name__ == '__main__':
   retval = main()
   sys.exit( retval )
