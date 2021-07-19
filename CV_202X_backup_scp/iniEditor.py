#! /usr/bin/env python
#
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
#
# Tool to modify key and password settings for backup.ini

from cryptography.fernet import Fernet
import argparse
import iniparse
import os

def decryptPwd (encryptdPwd, keyfile):
    # Decrypt Password using key value in file
    with open(keyfile,"rb") as keyFile: # Retrieves key
        Ekey = keyFile.read()
    fE = Fernet(Ekey)
    return fE.decrypt(encryptdPwd)

def encryptPwd (passwd, keyfile):
    # Encrypt Password using key value in file
    with open(keyfile,"rb") as keyFile: # Retrieves key
        key = keyFile.read()
    fE = Fernet(key)
    return fE.encrypt(passwd)

def chngPasswd(encryptdPwd,keyFile):
    newEncryptPwd = False
    change = raw_input("   Change Password : %s (y/n) " %(encryptdPwd))
    if "y" in change.lower():
        changePwd = True
        currentPwd = decryptPwd(encryptdPwd, keyFile)
    else:
        changePwd = False
    while changePwd:
        password = raw_input("   Please enter current password: ")
        if str(currentPwd) == str(password):
            newPwd = raw_input("   Please enter new password ")
            print ("   Password %s changed to %s " %(currentPwd, newPwd))
            proceed = raw_input("   Would you like to apply change? (y/n) ")
            if "y" in proceed.lower():
                newEncryptPwd = encryptPwd(newPwd, keyFile)
            changePwd = False
        else:
            print ("   Passwords did not match,")
            tryAgain = raw_input("   Do you want to try again? (y/n) ")
            if "n" in tryAgain.lower():
                changePwd = False
    print("")
    return newEncryptPwd

def chngKey(encyptdPwd, keyfile ):
    newKeyFile = False
    newPwd = False
    directory, filename = os.path.split(keyfile)
    change = raw_input("   Update Key / Key File : %s (y/n) " %(keyfile))
    if "y" in change.lower():
        changeKeyfile = True
        password = decryptPwd(encyptdPwd, keyfile)
    else:
        changeKeyfile = False
    while changeKeyfile:
        changeOption = raw_input("   (A)ssign new key file or (U)pdate Key ?(a/u) ")
        if "a" in changeOption.lower():
            newFile = raw_input("   Please enter full path and filename for key file ")
            if os.path.exists(newFile) and os.path.getsize(newFile) > 0:
                print ("   Updating current Password using new Key File")
                newPwd = encryptPwd(password,newFile)
                newKeyFile = str(newFile)
                changeKeyfile = False
            else:
                print ("   File %s does not exist - Please try again" %newKeyFile)
        elif "u" in changeOption.lower():
            backup = str(directory)+"backup.key"
            print ("   Backing up current key to %s " %backup)
            with open(keyfile,"rb") as keyFile: # Retrieves key
                ckey = keyFile.read()
            with open(backup, "wb") as keyFile:  # Opens the file the backup is to be written to
                keyFile.write(ckey)  # Writes the key
            print ("   Updating %s using new Key " %filename)
            # Generate the new key
            nkey = Fernet.generate_key()
            with open(keyfile, "wb") as keyFile:  # Opens the file the key is to be written to
                keyFile.write(nkey)  # Writes the key
            print ("   Updating current Password using new Key ")
            newPwd = encryptPwd(password,keyfile)
            changeKeyfile = False
        else:
            print ("   Bad Option please try again")
    print("")
    return [newKeyFile,newPwd]

def parseArgs():
    parser = argparse.ArgumentParser( description='Backup INI file editor' )
    parser.add_argument('--ini', default='./backup.ini', help='Ini file location, default to ./')
    args = parser.parse_args()
    return args

def main():
    options = parseArgs()
    
    # fetch the script options from the ini file
    iniFile = iniparse.ConfigParser()
    iniFile.read(options.ini)
    if iniFile.has_section("Server_Settings"): # Get Server optins from ini
        server_settings = {}
        for option, value in iniFile.items("Server_Settings"):
            server_settings[option]=value

        # List and edit Options
        print ("\n#####  Current Server Settings   #####\n")
        for option in server_settings:
            print(" %s : %s" %(option,server_settings[option]))
        print("")
        decision = raw_input("Would you like to edit these settings? (y/n) ")
        if "y" in decision.lower():
            print ("Change Value or hit Enter to use current\n")
            for option in server_settings:
                if option == "password":
                    if "keyfile" in server_settings.keys():
                        print(" %s : %s" %(option,server_settings[option]))
                        newPassword = chngPasswd(server_settings['password'],server_settings['keyfile'])
                        if newPassword:
                            server_settings['password'] = newPassword
                    else:
                        print (" %s : %s - MISSING KEY" %(option,server_settings[option]))
                elif option == "keyfile":
                    if "password" in server_settings.keys():
                        print("  %s : %s" %(option,server_settings[option]))
                        newKeyFile,newPwd = chngKey(server_settings['password'], server_settings['keyfile'])
                        if newPwd:
                            server_settings['password']= newPwd
                        if newKeyFile:
                            server_settings['keyfile'] = newKeyFile
                    else:
                        print (" %s : %s - MISSING PASSWORD" %(option,server_settings[option]))
                else:
                    change = raw_input(" %s : %s " %(option,server_settings[option]))
                    if change == "":
                        pass
                    else:
                        server_settings[option] = change
                        print ("  %s changed to %s" %(option,change))
            print ("\n\n#####  New Server Settings   #####\n")
            for option in server_settings:
                if option == "password":
                    if "keyfile" in server_settings.keys():
                        password = decryptPwd (server_settings[option],server_settings['keyfile'])
                        print (" %s : %s" %(option,server_settings[option]))
                    else:
                        print (" %s : %s - MISSING KEY" %(option,server_settings[option]))
                else:
                    print(" %s : %s" %(option,server_settings[option]))
            # Update INI file
            print ("\n\n#####  Updating %s Server_Settings  #####\n" %options.ini)
            for key in server_settings:
                iniFile.set("Server_Settings",key,server_settings[key])
            with open(options.ini, 'w') as fp:
                iniFile.write(fp)
    if iniFile.has_section("Backup_Settings"): # Get Backup options from ini
        backup_settings = {}
        for option, value in iniFile.items("Backup_Settings"):
            backup_settings[option]=value   
        # List and edit Options
        print ("\n #####  Current Backup Settings   #####\n")
        for option in backup_settings:
            print(" %s : %s" %(option,backup_settings[option]))
        print("")
        decision = raw_input("Would you like to edit these settings? (y/n) ")
        if "y" in decision.lower():
            print ("Change Value or hit Enter to use current\n")
            for option in backup_settings:
                change = raw_input(" %s : %s " %(option,backup_settings[option]))
                if change == "":
                    pass
                else:
                    backup_settings[option] = change
                    print ("  %s changed to %s" %(option,change))
            print ("\n\n#####  New Backup Settings   #####\n")
            for option in backup_settings:
                print(" %s : %s" %(option,backup_settings[option]))
            # Update INI file
            print ("\n\n#####  Updating %s Backup_Settings  #####\n" %options.ini)
            for key in backup_settings:
                iniFile.set("Backup_Settings",key,backup_settings[key])
            with open(options.ini, 'w') as fp:
                iniFile.write(fp)

if __name__ == '__main__':
   main()