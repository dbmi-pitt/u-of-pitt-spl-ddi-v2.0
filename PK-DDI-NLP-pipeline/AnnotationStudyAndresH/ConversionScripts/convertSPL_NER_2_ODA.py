#!/usr/bin/python
#
# convertSPL_NER_2_ODA.py
#
# Convert NER output to Open Data Annotation serialized in JSON and
# output a CSV file containing the preferred name, exact string, and
# URIs of all drug mentions
#
# Author: Richard Boyce and Andres Hernandez

# Copyright (C) 2012-2014 by Richard Boyce and the University of Pittsburgh
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
from os import walk

############################################################
# Customizations

PREFIX_SUFFIX_SPAN = 30

# The path of JSON objects produced the the SPL NER extraction program
dirpath = '../json-objects/'

# Base folder underwhich 
inputProductLabels = '../input-files/'


############################################################
filesPddi = []

for (jsondir, dirnames, filenames) in walk(dirpath):
    filesPddi.extend(filenames)
    break

drugList = []
for fileName in filesPddi[:]:
    with open(dirpath+fileName,'r') as jsonInputFile:
        jsonObject = json.load(jsonInputFile)        
        fileIdpre = fileName.replace("package-insert-section-", "")
        fileId = fileIdpre.replace(".txt-PROCESSED.xml.json","")
        
        for element in jsonObject:
            jsonDict = {}
            jsonDict['fileId'] = fileId
            jsonDict['name'] = element['preferredName']
            jsonDict['fullId'] = element['fullId']
            jsonDict['fro'] = element['fro']
            jsonDict['to'] = element['to']
            
            # TODO: this is because abbreviations added by NER have no
            # URIs at this time. Fix!
            if element['fullId'] == "Added locally":
                continue

            fullIdElement = element['fullId'].split('/')
            jsonDict['drugType'] = fullIdElement[-2].strip()
            jsonDict['drugCUI'] = fullIdElement[-1].strip()
            drugList.append(jsonDict)

drugInfoList = []

for element in drugList:
    drugInfo = dict(element)
    labelFile = open(inputProductLabels + 'package-insert-section-'+element['fileId']+'.txt','r')
    drugLabel = labelFile.read().decode('utf-8')

    if len(range(0,int(element['fro']))) < PREFIX_SUFFIX_SPAN:
        drugInfo['prefix'] = drugLabel[0:int(element['fro'])-1]
    else:
        drugInfo['prefix'] = drugLabel[int(element['fro'])-PREFIX_SUFFIX_SPAN:int(element['fro'])-1]

    drugInfo['exact'] = drugLabel[int(element['fro'])-1:int(element['to'])]

    if len(range(int(element['to']),len(drugLabel))) < PREFIX_SUFFIX_SPAN:
        drugInfo['suffix'] = drugLabel[int(element['to']):]
    else:
        drugInfo['suffix'] = drugLabel[int(element['to']):int(element['to'])+PREFIX_SUFFIX_SPAN]

    drugInfoList.append(drugInfo)


with open('drug_list.json', 'w') as nerOutput:
    json.dump(drugInfoList, nerOutput)

with open('NER-output.csv','w') as nerOutput:
    for element in drugInfoList:
        line = str(element['fileId'])+';'+str(element['name'])+';'+str(element['exact'])+';'+str(element['fullId'])
        print >>  nerOutput, line
