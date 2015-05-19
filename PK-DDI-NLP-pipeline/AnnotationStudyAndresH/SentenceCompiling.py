__author__ = 'amh211'

from itertools import groupby
import sys

if __name__=="__main__":

    fileId = sys.argv[1]
    dirpath = './'+fileId+'/'

    with open('./'+fileId+'.csv','r') as inFile:
        with open('./'+fileId+'-sentenceCompiled.csv', 'w') as outFile:
            currentLabel = inFile.readlines()
            tempInteractions = []

            for element in currentLabel[0:]:
                strippedLabel = element.rstrip()
                tempInteractions.append(strippedLabel.split('\t'))

            interactions = []
            for singleLine in tempInteractions:
                tempSingleInteraction = []
                tempSingleInteraction = [singleLine[0], singleLine[1].lower(), singleLine[2].lower()]
                tempSingleInteraction.extend(singleLine[3:])
                interactions.append(tempSingleInteraction)

            singleDocumentInteraction = []

            for key1, value1 in groupby(interactions, key=lambda t: t[0]):
                currentGroup = sorted(list(value1), key=lambda t: t[1])
                for key2, value2 in groupby(currentGroup, key=lambda t: t[1]):
                    currentInteractionG1 = sorted(list(value2), key=lambda t: t[2])
                    for key3, value3 in groupby(currentInteractionG1, key=lambda t: t[2]):
                        currentInteractionG2 = sorted(list(value3), key=lambda t: t[2])
                        singleDocumentInteraction.append(currentInteractionG2[0])
                        # for element in currentInteractionG2:
                        #     print element
                        # print '---------------------------------------------------------------------'

            # print 'final version'
            # print '---------------------------------------------------------------------'

            for index, value in enumerate(singleDocumentInteraction):
                for value2 in singleDocumentInteraction[index+1:]:
                    if value [0]==value2[0] and value [1]==value2[2] and value [2]==value2[1]:
                        # print index, value[0:3], value2[0:3]
                        singleDocumentInteraction.pop(index)
                        break

            print '---------------------------------------------------------------------'

            trueInterations = []
            for value in singleDocumentInteraction:
                if value[5] == 'true':
                    trueInterations.append(value)

            for index, value in enumerate(trueInterations):
                print >> outFile, "\t".join(value)

            print 'total number of true interactions:', len(trueInterations)

    print 'finished'
