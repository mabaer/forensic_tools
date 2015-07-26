#!/usr/bin/python
# This script prints the IPs that are likely natted using the TCP timestamp option.
# The script invokes tshark and gets as parameter a pcap file.
# Copyright 2015 Marc-André Bär

import sys
import subprocess

listIPs=[]
listNattedIPs=[]

#Returns number of frames
def getFrameCount(frames):
    return frames.count('\n')

#Checks an ip
def checkIP(ip, frames, count):
	global listNattedIPs
	avgRelation=0.0
	relation=0.0
	lasttime=0
	lastTSval=0
	c=0
	for i in range(count):
		frame=frames[i].split()
		if frame[0] == ip:
			#If it is the first frame just set values
			if lasttime == 0:
				lasttime=frame[1]
				lastTSval=frame[2]
			else:
				#If it is a frame bigger 2 check if the relation fits to the average
				if(c>0 and lastTSval != frame[2]):
					relation = float((float(frame[1])-float(lasttime)))/(float(float(frame[2])-float(lastTSval)))
					#Check if relation fits with the average
					absdiff=abs(relation-avgRelation)
					#More Finetuning possible if necessary.
					maxdiff=avgRelation
					#If the difference is bigger than the allowed max or a negativ relation is measured the ip will be marked as natted
					if(absdiff > maxdiff or relation < 0):
						#if the timestamp is to close to the maximumg (4294967296) we will not count the fraame because an overflow would lead to wrong calculations
						if(frame[2] < 4294966796 or frame[2] > 500):
							listNattedIPs.append(ip)
							break
						
					#Update average
					c += 1
					avgRelation=float(avgRelation*float((c-1)/float(c))+relation*float(1/float(c)))
				#If it is the second frame just calculate the relation
				elif lastTSval != frame[2]:
					c += 1
					avgRelation = float((float(frame[1])-float(lasttime)))/(float(float(frame[2])-float(lastTSval)))
				#Update last values
				lasttime=frame[1]
				lastTSval=frame[2]					

def main():
    if len (sys.argv) != 2 :
            print "Use as argument PCAP_File"
            sys.exit (1)
    filename = sys.argv[1]
    #Receive necessary data from the pcap file
    #tshark -r capture.pcap -e ip.src -e frame.time_relative -e tcp.options.timestamp.tsval -T fields
    process = subprocess.Popen(['tshark','-r',filename, '-e', 'ip.src', '-e', 'frame.time_relative', '-e', 'tcp.options.timestamp.tsval', '-T', 'fields'],stdout=subprocess.PIPE)
    output = process.communicate()[0]
    frames = output.splitlines()
    count=getFrameCount(output)
    #Iterate over frames
    for i in range(count):
        frame=frames[i].split()
        #If IP adress was not checked yet => Check it
        if frame[0] not in listIPs:
            listIPs.append(frame[0])
            checkIP(frame[0], frames, count)
    
    print("The natted IP adresses are:")
    print '\n'.join(listNattedIPs)

if __name__ == '__main__':
    main()