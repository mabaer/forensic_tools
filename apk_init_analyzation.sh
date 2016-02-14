#!/bin/bash
#
# APK initialize analyzation
#
# For the initialization process for starting an analyzation of a new APK file.
#
# Unpacks and performs all necessary steps and extracts first information about the file.
#
# Add the correct absolute path for all used tools!!!
#
# First parameter is the APK file and the second one is for the directory name of the analysis
# Assumptions made:
#	-Call script from the directory where the APK is located
# Copyright 2015 Marc-André Bär

APKFILE=$1
DESTINATION=$2
BAKSMALI='/root/softs/baksmali-2.0.8.jar'
AXMLPRINTER='/root/softs/AXMLPrinter2.jar'
DEX2JAR='/root/softs/dex2jar-2.0/d2j-dex2jar.sh'
CAMOUFLAGE='/root/softs/camouflage_checker.py'
MIMETYPES='/root/softs/apk_optim_mime.types'

extract_data() {
    	echo "### Start extraction of data:"
	echo "#Unzip"
	unzip $APKFILE -d $DESTINATION &>-
	rm -
	cd $DESTINATION
	echo "#GET AndroidManifest.xml.text"
	java -jar $AXMLPRINTER AndroidManifest.xml > AndroidManifest.xml.text
	echo "#GET Smali files"
	java -jar $BAKSMALI -o output "../$APKFILE"
	echo "#GET Jar file"
	$DEX2JAR classes.dex &>-
	rm -
	cd ..
	echo "### Finished extraction of data"
}

extract_info() {
    	echo "### Start extraction of information:"
	echo "#Certificate:"
	cd $DESTINATION
	openssl pkcs7 -inform DER -in META-INF/CERT.RSA -noout -print_certs -text
	echo " 	-Assets Dir:"
	python $CAMOUFLAGE assets/ $MIMETYPES
	echo "#Res Dir:"
	python $CAMOUFLAGE res/ $MIMETYPES
	echo "#GET Permissions:"
	egrep -o '".*permission\..*"' AndroidManifest.xml.text 
	egrep -o '".*vending\.B.*"' AndroidManifest.xml.text 
	cd ..
	echo "### Finished extraction of information"
}

extract_data
extract_info
