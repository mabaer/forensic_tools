#!/usr/bin/python
# This script lists number of pages that are different between two memory snapshots.
# The script uses volatility and takes as paramters two memory snapshot of a linux machine and the profile name. 
# Copyright 2015 Marc-André Bär

import sys
import os
import subprocess
import filecmp
import glob
import shutil

import volatility.conf as conf
config = conf.ConfObject()
import volatility.constants as constants
import volatility.registry as registry
import volatility.exceptions as exceptions
import volatility.obj as obj
import volatility.debug as debug

import volatility.addrspace as addrspace
import volatility.commands as commands
import volatility.scan as scan

from cStringIO import StringIO

def getDumps(img, profile, count):
	#Init
	config = conf.ConfObject()
	# Load up modules in case they set config options
	registry.PluginImporter()
	## Register all register_options for the various classes
	registry.register_global_options(config, commands.Command)
	registry.register_global_options(config, addrspace.BaseAddressSpace)
	## Parse all the options now
	config.parse_options(False)

	DUMPDIR="dumps"+str(count)
	if not os.path.exists(DUMPDIR):
		os.mkdir(DUMPDIR)

	config.PROFILE=profile
	config.LOCATION=str(img) #'file:///home/ubuntu/Desktop/volatility-2.4/'
	config.DUMP_DIR=DUMPDIR
	cmds = registry.get_plugin_classes(commands.Command, lower = True)

	profs = registry.get_plugin_classes(obj.Profile)
	if config.PROFILE not in profs:
		raise BaseException("Invalid profile " + config.PROFILE + " selected")	

	## Register the help cb from the command itself
	command = cmds['linux_dump_map'](config)
	config.parse_options()
	command.execute()

def printres(result):
	result.sort(key=lambda x: x[0])
	print("PID	Pages that matches	Pages that are different")
	for r in result:
		print(str(r[0])+"\t"+str(r[1])+"\t\t\t"+str(r[2])+"\t")

def cleanup():
	shutil.rmtree('dumps0')
	shutil.rmtree('dumps1')

def analysedumps():
	files1 = glob.glob("dumps0/*")
	files1.sort()
	files2 = glob.glob("dumps1/*")
	files2.sort()
	result = []
	donelist=[]
	i = 0
	while True:
		#Break condition
		if len(files1) <= i:
			break
		#get PID of file
		f = files1[i]
		start = f.find(".")
		end = f.find(".", start+1)
		pid=f[start+1:end]

		#If PID was already checked
		if pid in donelist:
			i += 1
			continue
		
		#Reset values
		matches= 0
		diff=0

		#Get files for pid from both dumps
		r = "dumps1/*."+str(pid)+".*"
		f_2list = glob.glob(r)
		r = "dumps0/*."+str(pid)+".*"
		for f_1 in glob.glob(r):
			#Check if file exists
			checkFile = "dumps1/"+f_1[7:]
			if checkFile in f_2list:
				#Compare both files
				if filecmp.cmp(f_1, checkFile):
					matches+=1
				else:
					diff+=1	
				f_2list.remove(checkFile)
			else:
				diff+=1		
		#Add new pages as difference and safe result
		diff+=len(f_2list)
		result.append([pid, matches, diff])
		donelist.append(pid)
		i += 1
		#For debug
		#if pid != "1":
		#	break
	return result

def main():
	if len (sys.argv) != 4 :
		print "Use as arguments DUMP1 DUMP2 PROFILENAME \nFor the DUMPS an absolute path is needed e.g. file:///home/ubuntu/Desktop/volatility-2.4/dump.lime"
		sys.exit (1)

	img1 = sys.argv[1]
	img2 = sys.argv[2]
	profilename = sys.argv[3]

	#Generate Dumps
	getDumps(img1, profilename, 0)
	getDumps(img2, profilename, 1)
	#Analyse pages
	res = analysedumps()
	#Print results and delete dump map files
	printres(res)
	cleanup()

if __name__ == '__main__':
    main()


