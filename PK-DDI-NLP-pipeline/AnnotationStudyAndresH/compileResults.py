__author__ = 'amh211'
from os import walk
import sys

if __name__=='__main__':
    fileId = sys.argv[1]
    dirpath = './'+fileId+'/'
    filesPddi = []

    for (dirpath, dirnames, filenames) in walk(dirpath):
        filesPddi.extend(filenames)
        break

    with open('./'+fileId+'.csv', 'w') as outfile:
        for filename in filenames:
            with open(dirpath + '/' + filename,'r') as inFile:
                pddiResult = inFile.read()
                pddiLines = pddiResult.split('\n')
                # print pddiLines
                for interaction in pddiLines:
                    if interaction != '|startresults' and interaction != '|endresults' and interaction!='':
                        print >> outfile, filename + '\t' + interaction

    print 'finished'