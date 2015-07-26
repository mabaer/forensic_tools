#!/usr/bin/python
# This script checks all the sector slack at the end of each file in a ext3 partition and dumps the ones that contain data.
# The script uses SleuthKit to check the sector slack. It takes as parameters an image and the imagefile type.
# Copyright 2015 Marc-André Bär

import os
import os.path
import sys
import subprocess
import re

cnt=0
files=[]

#Counts the number of files
def getFileCount():
	global files
	cnt=0
	for line in files:
		cnt += 1
	return cnt

#Checks the files
def checkFile(path, fs):		
    global cnt
    percentage=0
    cntWork=0
    oldpercentage=0
    for file in files:
        #Get inode num
        m=re.search('[^\d]+(\d+)', file)
        inode = m.group(1)
        #Check slack space
        process = subprocess.Popen(['icat','-s', '-f', fs ,path, str(inode)],stdout=subprocess.PIPE)
        slackbytes, err = process.communicate()
        process = subprocess.Popen(['icat', '-f', fs ,path,str(inode)],stdout=subprocess.PIPE)
        normalbytes, err = process.communicate()
        #Check difference between normalbytes and with additional slackbytes
        if(slackbytes != normalbytes):
            #Get just the slack bytes
            slackbytes=slackbytes[len(normalbytes):]
            #Check if a byte is not zero
            for byte in slackbytes:
                if byte != '\x00':
                    #Save info and create directory if necessary
                    if not os.path.exists("slackbytes"):
                        os.makedirs("slackbytes")
                    #Extract just the content and remove zeros
                    out=re.sub(r'[^\w]', '', slackbytes)
                    f = open("slackbytes/"+str(inode), "wb")	
                    f.write(out)
                    f.close()	
                    break				

        #Increas progress
        cntWork += 1
        percentage = cntWork/float(cnt)*100
        #Print new value if increase is big enough
        if(percentage >= oldpercentage+1):
            print("%.1f" % percentage + "%")
            oldpercentage=percentage
    print("Done!")

def main():
    global cnt
    global files
    if len (sys.argv) != 3 :
        print "Use as arguments IMAGE FILESYSTEM_TYPE e.g. python script2.py ext3-img-kw-1.dd ext3"
            sys.exit (1)
    process = subprocess.Popen(['fls','-F',sys.argv[1]],stdout=subprocess.PIPE)
    output = process.communicate()[0]
    files=output.splitlines()
    cnt=getFileCount()
    checkFile(sys.argv[1],sys.argv[2])

if __name__ == '__main__':
    main()
