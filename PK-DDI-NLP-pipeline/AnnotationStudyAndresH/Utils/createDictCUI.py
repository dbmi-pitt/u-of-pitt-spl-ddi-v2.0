if __name__ == '__main__':

    goldCUI = './goldStandardResults.csv'
    
    with open(goldCUI,'r') as goldFile:
        goldCUIFile = goldFile.readlines()
        
        dictCUI = {}

        for goldline in goldCUIFile[0:]:
            goldList = goldline.strip().split('\t')
            
            if len(goldList)==20:
                if goldList[2].strip().lower() not in dictCUI:
                    dictCUI[goldList[2].strip().lower()] = goldList[-2]
                if goldList[7].strip().lower() not in dictCUI:
                    dictCUI[goldList[7].strip().lower()] = goldList[-1]
      
    dictTemp = {}

    for element in dictCUI:
        if dictCUI[element] != '':
            dictTemp[element]=dictCUI[element]

    nlpCUI = './nlpResultsold.csv'

    with open(nlpCUI,'r') as NlpFile:
        goldCUIFile = NlpFile.readlines()
        
        for goldline in goldCUIFile[0:]:
            goldList = goldline.strip().split('\t')
            
            if len(goldList)==10:
                if goldList[1].strip().lower() not in dictTemp:
                    dictTemp[goldList[1].strip().lower()] = goldList[-2]
                if goldList[2].strip().lower() not in dictTemp:
                    dictTemp[goldList[2].strip().lower()] = goldList[-1]
    with open('./cuilist.csv', 'w') as cuifile:
        for element in dictTemp:
            print >> cuifile, str(element)+','+str(dictTemp[element])

