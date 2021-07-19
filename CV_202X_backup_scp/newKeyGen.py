#! /usr/bin/env python
#
# Copyright (c) 2021 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
#
# Tool to modify key and password settings for backup.ini

from cryptography.fernet import Fernet
import argparse
import iniparse

def encryptPwd (passwd, keyfile):
    # Encrypt Password using key value in file
    with open(keyfile,"rb") as keyFile: # Retrieves key
        key = keyFile.read()
    fE = Fernet(key)
    return fE.encrypt(passwd)

def newKey(keyfile):
    newEncryptPwd = False
    nkey = Fernet.generate_key()
    with open(keyfile, "wb") as keyFile:  # Opens the file the key is to be written to
        keyFile.write(nkey)  # Writes the key
    changePwd = True
    while changePwd:
        newPwd = raw_input("   Please enter password to encrypt: ")
        print ("   Password will be %s" %(newPwd))
        proceed = raw_input("   Would you like to apply change? (y/n) ")
        if "y" in proceed.lower():
            newEncryptPwd = encryptPwd(newPwd, keyfile)
            changePwd = False
        else:
            proceed = raw_input("   Would you like to try again? (y/n) ")
            if "n" in proceed.lower():
                changePwd = False
    return newEncryptPwd

def parseArgs():
    parser = argparse.ArgumentParser( description='Key File and Password genorator' )
    parser.add_argument('--ini', default='./backup.ini', help='Ini file location, default to ./backup.ini')
    args = parser.parse_args()
    return args

def main():
    options = parseArgs()
    # fetch the script options from the ini file
    iniFile = iniparse.ConfigParser()
    iniFile.read(options.ini)
    if iniFile.has_section("Server_Settings"): # Get Server optins from ini
        changeKey = True
        while changeKey:
            newKeyFile = raw_input("   Please enter New Key File name: ")
            print ("   Key File will be %s" %(newKeyFile))
            proceed = raw_input("   Would you like to create key and password? (y/n) ")
            if "y" in proceed.lower():
                newPassword = newKey(newKeyFile)
                if newPassword:
                    iniFile.set("Server_Settings","keyFile",newKeyFile)
                    iniFile.set("Server_Settings","password",newPassword)
                    with open(options.ini, 'w') as fp:
                        iniFile.write(fp)
                    print ("   Key File and Password have been updated")
                    print ("   new Key File is %s" %newKeyFile)
                    print ("   Server_settings in %s have been updated" %options.ini)
                    changeKey = False
                else:
                    print(" Problem with key generation and password")
                    proceed = raw_input("   Would you like to try again? (y/n) ")
                    if "n" in proceed.lower():
                        changeKey = False
            else:
                proceed = raw_input("   Would you like to try again? (y/n) ")
                if "n" in proceed.lower():
                    changeKey = False
    else:
        print(" Ini file is missing Server_Settings section\nPlease check: %s is the INI file for the backup scrip" %options.ini)

if __name__ == '__main__':
   main()
            