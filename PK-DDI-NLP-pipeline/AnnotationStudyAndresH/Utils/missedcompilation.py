__author__ = 'amh211'
from os import walk

if __name__=='__main__':

    dirpath = './logsconversion'
    filesmissed = []
    for (dirpath, dirnames, filenames) in walk(dirpath):
        filesmissed.extend(filenames)
        break

    with open('./logsconversion/summarymissed.csv', 'w') as outfile:
        for filename in filesmissed:
            with open(dirpath + '/' + filename,'r') as inFile:
                missedCode = inFile.readlines()
                for line in missedCode:
                    listLine = line.strip().split('\t')
                    print listLine
