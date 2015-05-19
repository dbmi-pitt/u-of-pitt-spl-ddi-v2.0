__author__ = 'amh211'

from itertools import groupby
import sys

if __name__=="__main__":

    with open('./cuilist.csv','r') as cuiFile:
        currentCUI = cuiFile.readlines()
        dictCUIs = {}

        for element in currentCUI[0:]:
            strippedLabel = element.strip()
            dictCUIs[strippedLabel.split(',')[0]]=strippedLabel.split(',')[1]
    
    print dictCUIs

    fileId = sys.argv[1]
    dirpath = './'+fileId+'/'

    with open('./'+fileId+'-sentenceCompiled.csv','r') as inFile:
        with open('./'+fileId+'-performance.csv', 'w') as outFile:
            currentLabel = inFile.readlines()
            tempInteractions = []

            for element in currentLabel[0:]:
                LineLabel = element.strip()
                strippedLabel = LineLabel.split('\t')
                
                if strippedLabel[1] in dictCUIs:
                    strippedLabel.append(dictCUIs[strippedLabel[1]])
                else:
                    strippedLabel.append('')
                    
                if strippedLabel[2] in dictCUIs:
                    strippedLabel.append(dictCUIs[strippedLabel[2]])
                else:
                    strippedLabel.append('')
                #print "\t".join(strippedLabel)
                print >> outFile, "\t".join(strippedLabel)
