import sys

if __name__=="__main__":

    fileId = sys.argv[1]
    dirpath = './'+fileId+'/'

    with open('./cuilist.csv', 'r') as cuiFile:
        currentCui = cuiFile.readlines()
        dictTerms = {}

        for element in currentCui[0:]:
            strippedLabel = element.strip()
            dictTerms[strippedLabel.split(',')[0]]=strippedLabel.split(',')[1]

    print dictTerms

    with open('./'+fileId+'-sentenceCompiled.csv', 'r') as inFile:
        with open('./'+fileId+'-performance.csv','w') as outFile:
            currentLabel = inFile.readlines()
            tempInteractions = []

            for element in currentLabel[0:]:
                strippedLabel = element.strip()
                tempInteractions.append(strippedLabel.split('\t'))
                print tempInteractions 



