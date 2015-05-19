__author__ = 'amh211'

from subprocess import call

if __name__=='__main__':

    with open('./postprocessed-ids.txt','r') as inFile:
        currentIds = inFile.read()
        singleIds = currentIds.split('\n')

        for line in singleIds[0:-1]:
            drugLabel = line.split('\t')
            print drugLabel[0]
            shellString = 'python RmConceptDuplicates.py pitt ' + drugLabel[0]
            call(shellString, shell=True)

    print 'finished'
