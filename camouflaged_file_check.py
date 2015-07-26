#!/usr/bin/python
# This script detects camouflaged files.
# The script uses the python magic bindings and compares the results with the mime types. As parameters it takes a directory where to start recursively and optional an individual mime type file.
# Copyright 2015 Marc-André Bär

import sys
import os
import magic

mimefile = "/etc/mime.types"
count = 0

def compareMimeExt(file, mime, ext, mimefiletxt):
	global count
	pos = mimefiletxt.find(mime)
	possibleExt = [] 
	#Get all possible extensions
	while pos != -1:
		start = mimefiletxt.find(mime, pos) + len(mime)
		end = mimefiletxt.find("\n", start)
		possibleExt.extend(mimefiletxt[start:end].split())
		pos = mimefiletxt.find(mime, end)
	# Check all extensions
	for e in possibleExt:
		if e == ext:
			# Return if correct extension was found
			return
	# Print warning for camouflaged file
	print("Camouflaged file found! File " + file + " has extension " + ext + " as type " + mime)
	count += 1

def checkFile(filePath, mimefiletxt):
	# Get file mime
	m = magic.open(magic.MAGIC_MIME)
	m.load()
	mtype = m.file(filePath)
	endmime = mtype.find(';')
	# Get file extension
	extension = os.path.splitext(filePath)[1]
	#Compare type with extension if file has an extension	
	if extension[1:] != "":
		compareMimeExt(filePath, mtype[:endmime], extension[1:], mimefiletxt)

def checkDirectory(currentDir, mimefiletxt):
	for filename in next(os.walk(currentDir))[2]:
		# Check for camouflaged file
		checkFile(currentDir+filename, mimefiletxt)
	for subdir in next(os.walk(currentDir))[1]:
		# Check next directory
		checkDirectory(currentDir+subdir+"/", mimefiletxt)

def main():
    global mimefile
    if len (sys.argv) != 3 and len (sys.argv) != 2 :
        print "Use as arguments DIR [MIME_FILE]"
            sys.exit (1)
    #Check if user wants to use a different mime file
    if len(sys.argv) == 3 :
        print "Individual mime file used!"
        mimefile = sys.argv[2]

    #Start search
    file = open(mimefile, 'r')
    mimefiletxt = file.read()
    checkDirectory(sys.argv[1], mimefiletxt)
    if count == 0:
        print("No camouflaged files found")

if __name__ == '__main__':
    main()