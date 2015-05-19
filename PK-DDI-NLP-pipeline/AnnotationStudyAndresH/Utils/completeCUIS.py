if __name__ == '__main__':

	goldCUI = './Utils/performance/nlpResults.csv'
	with open(goldCUI,'r') as goldFile:
		goldCUIFile = goldFile.readlines()

		dictRXCUIS = {}

		for goldline in goldCUIFile[0:]:
			goldList = goldline.strip().split('\t')
			
			if goldList[1] not in dictRXCUIS:
				dictRXCUIS[goldList[1].strip().lower()] = goldList[-2].strip()
			
			if goldList[2] not in dictRXCUIS:
				dictRXCUIS[goldList[2].strip().lower()] = goldList[-1].strip()
			
			# print dictRXCUIS.keys()

	cuipath = './performance/postprocessedResults.csv'
	cuioutpath = './performance/postprocessedResults-output.csv'

	with open(cuipath,'r') as cuiFile:
		with open(cuioutpath,'w') as cuiOutFile:

			cuiText = cuiFile.readlines()
			for cuiLine in cuiText[0:]:
				
				cuiList = cuiLine.strip().split('\t')

				if cuiList[1].lower() in dictRXCUIS:  
					cuiList.append(dictRXCUIS[cuiList[1].lower()])
				else:
					cuiList.append(' ')
				
				if cuiList[2].lower() in dictRXCUIS:
					cuiList.append(dictRXCUIS[cuiList[2].lower()])
				else:
					cuiList.append(' ')

				# cuiList.append(dictRXCUIS[cuiList[1].lower()])
				# cuiList.append(dictRXCUIS[cuiList[1].lower()])
				
				print >> cuiOutFile, "\t".join(cuiList)


	print 'finished'
