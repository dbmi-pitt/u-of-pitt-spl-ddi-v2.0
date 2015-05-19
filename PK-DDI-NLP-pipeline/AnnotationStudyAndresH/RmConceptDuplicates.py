__author__ = 'amh211'

import string
import json
import re
import suds
import MySQLdb as mdb
import sys

WSDL_CACHE = False

class RxNormClient:
    def __init__(self):
        rxHost = "http://mor.nlm.nih.gov"
        rxURI = rxHost + "/axis/services/RxNormDBService?WSDL"
        self.client = suds.client.Client(rxURI)
        # print self.client

    def getCUI(self, name):
        return self.client.service.findRxcuiByString(name)

    def getDrugProperties(self, cui):
        return self.client.service.getRxConceptProperties(cui)

class databaseManager:
        def __init__(self, user, pswd, database):
            try:
                self.con = mdb.connect('localhost', user, pswd, database)
                self.cur = self.con.cursor()
                self.cur.execute("SELECT VERSION()")
                self.ver = self.cur.fetchone()
                # print "Database version : %s " % self.ver

            except mdb.Error, e:
                # print "Error %d: %s" % (e.args[0],e.args[1])
                sys.exit(1)

        def queryConcept(self, retrievedField, table, field, term):
            sqlStatement = "SELECT " + str(retrievedField) + " FROM " + str(table) + " WHERE " + str(field) + "=" + str(term) + " AND SAB='RXNORM';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            return self.cur.fetchall()

        def meshToRxnorm(self, term):
            sqlStatement = "SELECT RXCUI, STR, SAB, CODE FROM RXNCONSO WHERE SAB='MSH' AND CODE='" + str(term) + "';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            # print self.cur.execute(sqlStatement)
            # print self.cur.fetchall()
            if self.cur.execute(sqlStatement)>0:
                return self.cur.fetchall()[0][0]
            else:
                return 0

        def getIngredient(self, rel, rxcui):
            sqlStatement = "SELECT RXCUI2, RUI FROM RXNREL WHERE RELA=" + "'" + rel + "'" + " AND RXCUI1='" + str(rxcui) + "';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            # print self.cur.execute(sqlStatement)
            # print self.cur.fetchall()
            if self.cur.execute(sqlStatement)>0:
                return self.cur.fetchall()[0][0]
            else:
                return 0

if __name__=='__main__':
    print 'processing', sys.argv[2], 'file'

    fileId = sys.argv[2]
    #pddiInputPath = './pddi-output/'+ fileId +'--PK-DDIs.txt'
    pddiInputPath = './pddi-output/'+ fileId +'-PK-DDIs.txt'
    jsonInput = './json-objects/'+ fileId +'.txt-PROCESSED.xml.json'
    rawFilePath = './input-files/'+ fileId +'.txt'

    print pddiInputPath, jsonInput, rawFilePath

    if sys.argv[1] == 'local':
        mysqlSearch = databaseManager('root', 'karencita', 'rxnorm')
    elif sys.argv[1] == 'pitt':
        mysqlSearch = databaseManager('amh211', 'annotationstudy', 'rxnorm')

    with open(pddiInputPath,'r') as inFile:
        with open(jsonInput, 'r') as jsonInputFile:
            with open(rawFilePath, 'r') as outFile:
                jsonObject = json.load(jsonInputFile)
                pddiResult = inFile.read()
                pddiLines = pddiResult.split('\n')
                outFileText = outFile.read()
                outFileLines = outFileText.split('\n')

                dictDrugsNames = {}
                missedDrugNames = {}
                complList = []
                missedElements = 0

                logConvertFile = open('./logsconversion/log-files'+fileId+'-conversion-log.txt','w')
                jsonproblems = open('./json-issues.txt','w')

                for element in jsonObject:
                    tempList = []
                    drugInText = outFileText[int(element['fro'])-1:int(element['to'])]
                    # print element

                    # getting the drug type
                    # name = element['preferredName']
                    name = drugInText
                    tempType = element['fullId']
                    if tempType == "Added locally":
                        RXCUI = 'MESHNOTFOUND' # these elements cannot be mapped to rxnorm at this time. TODO: fix!
                    else:
                        fullIdElement = tempType.split('/')
                        drugType = fullIdElement[-2].strip()
                        drugCUI = fullIdElement[-1].strip()
                        # print drugType, drugCUI
                        missedDrugNames[name] = [str(tempType), str(drugType), str(drugCUI)]

                        if drugType != 'RXNORM':
                            if mysqlSearch.meshToRxnorm(drugCUI.strip()) != 0:
                                RXCUI = mysqlSearch.meshToRxnorm(drugCUI.strip())
                            else:
                                RXCUI = 'MESHNOTFOUND' # for elements that cannot be mapped to rxnorm
                                missedElements += 1
                                print >> logConvertFile, str(drugInText.strip())+'\t'+str(tempType)+'\t'+str(drugType)+'\t'+str(drugCUI.strip())
                                # print drugInText.strip(), tempType, drugType, drugCUI.strip(), 'NOTFOUND'
                        else:
                            RXCUI = drugCUI

                    key = drugInText #select the key that you want for the dictionary
                    if RXCUI != 'MESHNOTFOUND':
                        # print RXCUI, 'added'
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', RXCUI)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', RXCUI)
                        #currentResult = [RXCUI, conceptString, conceptType, drugInText, drugType, drugCUI, element['to'], element['fro'], element['fullId'], element['preferredName']]
                        currentResult = [RXCUI, conceptString, conceptType, drugInText, drugType, drugCUI, element['to'], element['fro'], element['fullId'], element['preferredName']]
                        if key in dictDrugsNames.keys():
                            dictDrugsNames[key].append(currentResult)
                        else:
                            dictDrugsNames[key] = [currentResult]

                # print dictDrugsNames.keys()
                # print missedDrugNames.keys()
                extendedJson = []

                for element in dictDrugsNames:
                    tempJsonObject = {}
                    for nestedelement in dictDrugsNames[element]:
                        tempJsonObject['rxCui'] = nestedelement[0]
                        tempJsonObject['rxConcept'] = nestedelement[1][0][0]
                        tempJsonObject['rxConceptType'] = nestedelement[2][0][0]
                        tempJsonObject['mentionInText'] = nestedelement[3]
                        tempJsonObject['sourceTerm'] = nestedelement[4]
                        tempJsonObject['sourceCui'] = nestedelement[5]
                        tempJsonObject['to'] = nestedelement[6]
                        tempJsonObject['fro'] = nestedelement[7]
                        tempJsonObject['fullId'] = nestedelement[8]
                        tempJsonObject['preferredName'] = nestedelement[9]
                        # print tempJsonObject
                        extendedJson.append(tempJsonObject)

                normalizedJson = []
                for element in extendedJson:
                    tempJsonObject = {}
                    key = element['mentionInText']

                    if element['rxConceptType']=='IN':
                        # print element['rxCui'], element['rxConcept'],' Ingredient'
                        # key = element['mentionInText']
                        currentResult = [element['rxCui'], element['rxConcept'], element['rxConceptType'], element['mentionInText'], element['sourceTerm'], element['sourceCui'],  element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)
                    elif element['rxConceptType']=='SCDG':
                        # print element['rxCui'], element['rxConcept'],'Semantic Clinical Dose Form Group '
                        nomrRxCui = mysqlSearch.getIngredient('isa', element['rxCui'])
                        # nomrRxCui = mysqlSearch.getIngredient('ingredient_of', element['rxCui'])
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        currentResult = [nomrRxCui, conceptString, conceptType, element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        # key = element['mentionInText']
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)
                    elif element['rxConceptType']=='PIN':
                        # print element['rxCui'], element['rxConcept'],'Precise Ingredient'
                        # print mysqlSearch.getIngredient('has_form', element['rxCui'])
                        # print mysqlSearch.getIngredient('form_of', element['rxCui'])
                        nomrRxCui = mysqlSearch.getIngredient('has_form', element['rxCui'])
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        currentResult = [nomrRxCui, conceptString, conceptType, element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)
                    ##FOR FUTURE USE INCLUDE OTHER RELATIONS
                    elif element['rxConceptType']=='BN':
                        # print element['rxCui'], element['rxConcept'],'Semantic Branded Dose Form Group'
                        # print mysqlSearch.getIngredient('form_of', element['rxCui'])
                        nomrRxCui = mysqlSearch.getIngredient('tradename_of', element['rxCui'])
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        currentResult = [nomrRxCui, conceptString, conceptType, element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)
                    else:
                        # print element['rxCui'], element['rxConcept'],' Ingredient'
                        key = element['mentionInText']
                        currentResult = [element['rxCui'], element['rxConcept'], element['rxConceptType'], element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)

                    # elif element['rxConceptType']=='DFG':
                    #     print element['rxCui'], element['rxConcept'],'Dose Form Group '
                    #     print mysqlSearch.getIngredient('form_of', element['rxCui'])

                    # print normalizedJson
                    mappingToRxnorm = {}
                    for element in normalizedJson:
                        if element.keys() in mappingToRxnorm.keys():
                            if element.values()[0][0] != mappingToRxnorm[element.keys()]:
                                print 'rxcui inconsistence'
                        else:
                            mappingToRxnorm[element.keys()[0]]=element.values()[0][0]

                # print mappingToRxnorm

                logFile = open('./logs/log-files'+fileId+'--log.txt','w')
                for listNorm in normalizedJson:
                    for key in listNorm:
                        print >>logFile,'1:','KEY:',key,'*** RXCUI ----->',listNorm[key][0]
                        print >>logFile,'2:','KEY:',key,'*** Concept from RXNORM ----->',listNorm[key][1]
                        print >>logFile,'3:','KEY:',key,'*** Concept Type ----->',listNorm[key][2]
                        print >>logFile,'4:','KEY:',key,'*** Drug mention in text ----->',listNorm[key][3]
                        print >>logFile,'5:','KEY:',key,'*** Source language ----->',listNorm[key][4]
                        print >>logFile,'6','KEY:',key,'*** CUI CODE in original terminology ----->',listNorm[key][5]
                        print >>logFile,'7:','KEY:',key,'*** Final position in text according to JSON Object ----->',listNorm[key][6]
                        print >>logFile,'8:','KEY:',key,'*** Initial position according to JSON Object ----->',listNorm[key][7]
                        print >>logFile,'9:','KEY:',key,'*** Full ID according to JSON Object ----->',listNorm[key][8]
                        print >>logFile,'10:','KEY:',key,'*** Preferred name according to JSON Object ----->',listNorm[key][9]
                        print >>logFile,'---------------------------------------------------------'

                # for element in dictDrugsNames.keys():
                    # print element, dictDrugsNames[element]

                # drugRetrieval = RxNormClient()
                dictDrugCuis = {}

                #Removing duplications - level 1: Using RxNorm Active Ingredients
                nlpPostProcessed_l1 = []

                totalInteractions = 0
                # print pddiLines

                # print mappingToRxnorm.keys()
                for line in pddiLines:
                    totalInteractions += 1
                    interaction = line.split('\t')
                    if len(interaction)>1:
                        # print interaction
                        drugOne = interaction[0].strip()
                        drugTwo = interaction[1].strip()
                        # print drugOne, 'vs.', drugTwo
                        # print mappingToRxnorm[drugOne], ' vs.',mappingToRxnorm[drugTwo]
                        if drugOne in mappingToRxnorm.keys() and drugTwo in mappingToRxnorm.keys():
                            if mappingToRxnorm[drugOne] != mappingToRxnorm[drugTwo]:
                                interaction.extend([str(mappingToRxnorm[drugOne]),str(mappingToRxnorm[drugTwo])])
                                nlpPostProcessed_l1.append(interaction)
                        elif (drugOne in mappingToRxnorm) and (drugTwo not in mappingToRxnorm):
                            interaction.extend([str(mappingToRxnorm[drugOne]),'none'])
                            nlpPostProcessed_l1.append(interaction)
                        elif (drugOne not in mappingToRxnorm) and (drugTwo in mappingToRxnorm):
                            interaction.extend(['none', str(mappingToRxnorm[drugTwo])])
                            nlpPostProcessed_l1.append(interaction)
                        elif (drugOne not in mappingToRxnorm) and (drugTwo not in mappingToRxnorm):
                            interaction.extend(['none','none'])
                        else:
                            interaction.extend(['none', 'none'])

                        if drugOne in missedDrugNames and drugTwo in missedDrugNames:
                            interaction.extend([str(missedDrugNames[drugOne][2]), str(missedDrugNames[drugTwo][2])])
                        elif drugOne in missedDrugNames and drugTwo not in missedDrugNames:
                            interaction.extend([str(missedDrugNames[drugOne][2]), 'none'])
                        elif drugOne not in missedDrugNames and drugTwo in missedDrugNames:
                            interaction.extend(['none', str(missedDrugNames[drugTwo][2])])
                        elif drugOne not in missedDrugNames and drugTwo not in missedDrugNames:
                            interaction.extend(['none', 'none'])
                        else:
                            interaction.extend(['none', 'none'])


                        nlpPostProcessed_l1.append(interaction)

                # Removing duplications - level 2: Using RxNorm Services
                nlpPostProcessed_l2 = []
                for interaction in nlpPostProcessed_l1:
                    if not re.match(interaction[0],interaction[1], flags=re.IGNORECASE):
                        nlpPostProcessed_l2.append(interaction)
                    else:
                        continue

    outFile = open('./pddi-postprocessed-output/'+fileId+'--pddi-postprocessed.txt','w')

    for line in nlpPostProcessed_l2:
        print >> outFile, "\t".join(line)

    with open(pddiInputPath,'r') as inFileNLP:
        pddiResult = inFileNLP.read()
        pddiLines = pddiResult.split('\n')
        nlp_CUI = []

        for line in pddiLines:
            totalInteractions += 1
            interaction = line.split('\t')
            if len(interaction)>1:
                # print interaction
                drugOne = interaction[0]
                drugTwo = interaction[1]
                # print drugOne, 'vs.', drugTwo
                # print mappingToRxnorm[drugOne], ' vs.',mappingToRxnorm[drugTwo]
                if drugOne in mappingToRxnorm.keys() and drugTwo in mappingToRxnorm.keys():
                    if mappingToRxnorm[drugOne] != mappingToRxnorm[drugTwo]:
                        interaction.extend([str(mappingToRxnorm[drugOne]),str(mappingToRxnorm[drugTwo])])
                        nlp_CUI.append(interaction)
                elif (drugOne in mappingToRxnorm) and (drugTwo not in mappingToRxnorm):
                    interaction.extend([str(mappingToRxnorm[drugOne]),'none'])
                    nlp_CUI.append(interaction)
                elif (drugOne not in mappingToRxnorm) and (drugTwo in mappingToRxnorm):
                    interaction.extend(['none', str(mappingToRxnorm[drugTwo])])
                    nlp_CUI.append(interaction)
                elif (drugOne not in mappingToRxnorm) and (drugTwo not in mappingToRxnorm):
                    interaction.extend(['none','none'])
                else:
                    interaction.extend(['none', 'none'])

                if drugOne in missedDrugNames and drugTwo in missedDrugNames:
                    interaction.extend([str(missedDrugNames[drugOne][2]), str(missedDrugNames[drugTwo][2])])
                elif drugOne in missedDrugNames and drugTwo not in missedDrugNames:
                    interaction.extend([str(missedDrugNames[drugOne][2]), 'none'])
                elif drugOne not in missedDrugNames and drugTwo in missedDrugNames:
                    interaction.extend(['none', str(missedDrugNames[drugTwo][2])])
                elif drugOne not in missedDrugNames and drugTwo not in missedDrugNames:
                    interaction.extend(['none', 'none'])
                else:
                    interaction.extend(['none', 'none'])

                nlp_CUI.append(interaction)

    NLPCUIFILE = open('./pddi-output-cui/'+fileId+'--pddi-cui.txt','w')

    for line in nlp_CUI:
        print >> NLPCUIFILE, "\t".join(line)

    print >>logFile, 'removed duplications', totalInteractions - len(nlpPostProcessed_l2)
    # print 'Normalized JSON Object:', len(normalizedJson), '\n', 'Original JSON Object:', len(jsonObject)
    print >>logFile, 'Number of missed JSON elements:', missedElements
