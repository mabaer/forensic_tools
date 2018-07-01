#!/usr/bin/python
# This script returns all stored WIFI passwords of a Windows system
# Copyright 2018 Marc-André Bär

import subprocess, sys, re

def getNetworks():
    # Get all WIFI profiles
    o=subprocess.Popen('netsh wlan show profiles', stdout=subprocess.PIPE)
    result = o.communicate()
    # Convert to utf-8 and ignore special characters like german umlaute
    utfResult = result[0].decode("utf-8", "ignore")
    # Extract all network profiles
    networks = re.findall(r" : (.*?)\r\n", utfResult)
    print("")
    print("Name - Password")
    print("---------------")
    print("")
    # Iterate over all detected networks and get the password
    for n in networks:
        pw = getPassword(n)
        print(n + " - " + pw)
        
# Gets a network name and extracts  the password  
def getPassword(networkName):
    # Get profile information
    request = 'netsh wlan show profile "' + networkName + '" key=clear'
    o=subprocess.Popen(request, stdout=subprocess.PIPE)
    result = o.communicate()
    # Convert to utf-8 and ignore special characters like german umlaute
    utfResult = result[0].decode("utf-8", "ignore")
    # Extract the password (English OS)
    password = re.findall(r"Key Content (.*?)\r\n", utfResult)
    if not password:
        # Extract the password (German OS)
        password = re.findall(r"sselinhalt (.*?)\r\n", utfResult)
    # Add more languages if necessary here
    if not password:
        return "NO PASSWORD"
    else:
        return password[0].split(' : ')[1]

def main():
    if len (sys.argv) != 1:
        print("No arguments are needed.")

    #Get WIFI Networks
    getNetworks()
    

if __name__ == '__main__':
    main()