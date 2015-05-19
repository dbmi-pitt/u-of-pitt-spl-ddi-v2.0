#!/usr/bin/python

import sys
import os
import string

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

drugName = sys.argv[1]
pathJson = "./AndresOutput/"+drugName+"jsonnameIDs.txt"
pathOutfiles = "./AndresOutput/"+drugName+"pddinlpoutputIDs.txt"

print pathJson
print pathOutfiles

fileJsonName = open(pathJson, "r")
# OR read all the lines into a list.
jsonList = fileJsonName.readlines()
jsonSet = set(jsonList)
# print len(jsonSet)
fileJsonName.close()

fileOutfiles = open(pathOutfiles, "r")
outList = fileOutfiles.readlines()
outSet = set(outList)
# print len(outSet)
fileOutfiles.close()

jsonDiff = jsonSet.symmetric_difference(outSet)
# print jsonDiff
# print len(jsonDiff)

dataUnion = jsonSet.intersection(outSet)
# print dataUnion
# print len(dataUnion)

pathJsonOut = "./AndresOutput/"+drugName+"Intersection.txt"
fileJsonName = open(pathJsonOut, "w+")
stringZip = ""
for element in dataUnion:
    fileJsonName.write(element)
    stringZip += string.rstrip(element) + ""
fileJsonName.close()

pathJsonOut = "./AndresOutput/"+drugName+"Differences.txt"
fileJsonName = open(pathJsonOut, "w+")
for element in jsonDiff:
    fileJsonName.write(element)
fileJsonName.close()
