## prepareRestart.py
#
# Prepare the pipeline for a restart when there may be SPLs that made
# through the NER or PDDI NLP stages
#
# Author: Richard D Boyce 
#
# 
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Library General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or (at your option) any later version.

## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Library General Public License for more details.

## You should have received a copy of the GNU Library General Public
## License along with this library; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.

import sys, shutil, datetime
import os.path
from os import walk

setids = None
try:
    f = open("setIDs.txt")
    s = f.read()
    s = s.strip()
    setids = s.split("\n")
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)

jsonContentFiles = []
for (dirpath, dirnames, filenames) in walk("json-output"):
    jsonContentFiles.extend(filenames)
    break

pddiContentFiles = []
for (dirpath, dirnames, filenames) in walk("pddi-nlp-output"):
    pddiContentFiles.extend(filenames)
    break

print "INFO: Current setids: %s\n\nSections that made it through the JSON stage: %s\n\nSections that made it through the PDDI extraction stage: %s" %(setids, jsonContentFiles, pddiContentFiles)

if len(jsonContentFiles) == 0 and len(pddiContentFiles) == 0:
	print "INFO: No section made it passed the NER stage to the JSON stage. A full restart is required. Proceed without changing the setids file."
	sys.exit(0)

print "INFO: Sections made it to the JSON or PDDI extraction stage."

# process sections that made it through to the PDDI extraction stage
if len(pddiContentFiles) > 0:
	setidsCopy = setids
	for setid in setidsCopy:
		foundPDDIL = filter(lambda x: x.find(setid) != -1, pddiContentFiles)
		foundJSONL = filter(lambda x: x.find(setid) != -1, jsonContentFiles)

		if foundPDDIL:
			print "INFO: Sections for setid %s made it through the PDDI extraction stage. Removing sections from the JSON stage. Data from the JSON stage will stored in backup/json-NER-data." % setid
			for pth in foundJSONL:
                            try:
				shutil.move("./json-output/%s" % pth,"./backup/json-NER-data/")
                            except shutil.Error as err:
                                print "WARNING: %s" % err

# reset the list of JSON files since some may have been moved to backup
jsonContentFiles = []
for (dirpath, dirnames, filenames) in walk("json-output"):
    jsonContentFiles.extend(filenames)
    break

if len(jsonContentFiles) > 0:
	setidsCopy = setids
        sectionContentFiles = []
        for (dirpath, dirnames, filenames) in walk("./tmp/infiles-for-NER"):
            sectionContentFiles.extend(filenames)
            break

	for setid in setidsCopy:
		foundJSONL = filter(lambda x: x.find(setid) != -1, jsonContentFiles)
		if foundJSONL:
			print "INFO: Sections for setid %s made it through the NER stage to the JSON stage but not through the PDDI extraction stage. Removing SPL sections with the setid from ./tmp/infiles-for-NER (files moved to /tmp) because this will prevent them from being reprocessed by the NER. JSON data from the NER stage will remain so it can be ran through the PDDI extraction stage." % setid
			sectionFilesL = filter(lambda x:x.find(setid) != -1, sectionContentFiles)
                        for pth in sectionFilesL:
                            try:
                                shutil.move("./tmp/infiles-for-NER/%s" % pth,"/tmp")
                            except shutil.Error as err:
                                print "WARNING: %s" % err
	

