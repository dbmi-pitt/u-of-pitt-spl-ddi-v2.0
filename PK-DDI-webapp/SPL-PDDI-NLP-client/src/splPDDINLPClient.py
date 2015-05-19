## splPDDINLPClient.py
#
# A simple client for the SPL PK DDI NLP extractor
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

import suds
import sys
import os.path, codecs
from os import walk
import simplejson as json
 
WSDL_CACHE = False
PARSER = "clear"

class Client:
    def __init__(self):
        self.client = suds.client.Client("http://localhost:12341/splPDDIExtractor/SPL_PDDI_NLP?wsdl")
               
        if WSDL_CACHE:
            self.client.options.cache.setduration(days = 1)            
        else:
            self.client.set_options(cache = None)

        self.client.set_options(timeout = 900)

 
    def getHello(self):
        return self.client.service.sayHello("dude!")
 
    def runPDDI_NLP(self, rawText, drugS):
        return self.client.service.testPddi(PARSER, rawText, drugS)
     
if(__name__ == "__main__"):
    if (len(sys.argv) == 5):
        setIdFile = str(sys.argv[1])
	splContentPath = str(sys.argv[2])
        jsonContentPath = str(sys.argv[3])
        outputFolder = str(sys.argv[4])

    else:
	print """ERROR: please call this program with four parameters: 
  1) path to a text file with setids, one per line
  2) path a folder with text from sections taken from the SPLs corresponding to the setids 
  3) path to a folder with JSON data containing drug mentions identified by the SPL drug NER program
  4) path to a folder where output from this program will be written
."""
	sys.exit(1)


    client = Client()
    
    ## uncomment to debug the web service
    #hello = client.getHello()
    #print hello
    setids = None
    try:
        f = open(setIdFile)
        s = f.read()
        s = s.strip()
        setids = s.split("\n")
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

    splContentFiles = []
    for (dirpath, dirnames, filenames) in walk(splContentPath):
        splContentFiles.extend(filenames)
        break

    jsonContentFiles = []
    for (dirpath, dirnames, filenames) in walk(jsonContentPath):
        jsonContentFiles.extend(filenames)
        break

    print "INFO: \n\tsetids: %s\n\tsplContentFiles: %s\n\tjsonContentFiles: %s" % (setids, splContentFiles, jsonContentFiles)

    for setid in setids:
        splfiles = filter(lambda x: x.find(setid) != -1, splContentFiles)
        jsonfiles = filter(lambda x: x.find(setid) != -1, jsonContentFiles)
        
        for splFile in splfiles:
            print splFile
            f = codecs.open(os.path.join(splContentPath, splFile),'r','utf_8')
            rawText = f.read()
            f.close()
            #print rawText # might trigger unicode error

            section = splFile.replace(setid,"").replace(".txt","").replace("-","")
            print "\n%s\n" % section

            jsonFileL = filter(lambda x: x.find(section + ".txt") != -1, jsonfiles)
            if len(jsonFileL) == 0:
                print "ERROR: unable to find json data for splFile %s. Skipping this SPL section" % splFile
                continue

            jsonFile = jsonFileL[0]
            print "%s" % jsonFile
            f = open(os.path.join(jsonContentPath, jsonFile),'r')
            dictL = json.load(f)
            f.close()            
            print "%s" % dictL
            
            drugMentionsD = {}
            for elt in dictL:
                fro = int(elt['fro']) - 1
                to = int(elt['to'])
                mentionD = {'fro':fro, 'to':to, 'uri':elt['fullId'], 'preferredName':elt['preferredName']}
                
                # grab the original string that NER recognized for
                # those cases where the NER did not identify an
                # abbreviation
                if mentionD['uri'] == "Added locally":
                    drugMention = mentionD['preferredName']
                else:
                    drugMention = rawText[fro:to]
              
                if drugMentionsD.has_key(drugMention):
                    drugMentionsD[drugMention].append(mentionD)
                else:
                    drugMentionsD[drugMention] = [mentionD]

            print "%s" % drugMentionsD.keys()

            drugS = ":".join(drugMentionsD.keys())
            print drugS
            
            nlpOut = client.runPDDI_NLP(rawText, drugS)
            outFName = "%s-%s-PK-DDIs.txt" % (setid, section)
            outpath = os.path.join(outputFolder, outFName)
            f = codecs.open(outpath,'w','utf_8')
            f.write(nlpOut)
            f.close()
            
            print "INFO: wrote extracted PK DDIs to %s" % outpath
            print "WARNING: Be sure to follow this step with a process that further filters the output PDDIs to drop all lines for which the preferredName of the  two drug mentions is the same since these are just duplicate mentions."
