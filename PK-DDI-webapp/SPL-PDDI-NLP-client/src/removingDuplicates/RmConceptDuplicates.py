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
                print "Database version : %s " % self.ver

            except mdb.Error, e:
                print "Error %d: %s" % (e.args[0],e.args[1])
                sys.exit(1)

        def queryConcept(self, retrievedField, table, field, term):
            sqlStatement = "SELECT " + retrievedField + " FROM " + table + " WHERE " + field + "=" + term + " AND SAB='RXNORM';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            return self.cur.fetchall()

        def meshToRxnorm(self, term):
            sqlStatement = "SELECT RXCUI, STR, SAB, CODE FROM RXNCONSO WHERE SAB='MSH' AND CODE='" + term + "';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            # print self.cur.execute(sqlStatement)
            # print self.cur.fetchall()
            if self.cur.execute(sqlStatement)>0:
                return self.cur.fetchall()[0][0]
            else:
                return 0

        def getIngredient(self, rel, rxcui):
            sqlStatement = "SELECT RXCUI2, RUI FROM RXNREL WHERE RELA=" + "'" + rel + "'" + " AND RXCUI1='" + rxcui + "';"
            # print sqlStatement
            self.cur.execute(sqlStatement)
            # print self.cur.execute(sqlStatement)
            # print self.cur.fetchall()
            if self.cur.execute(sqlStatement)>0:
                return self.cur.fetchall()[0][0]
            else:
                return 0

if __name__=='__main__':

    inputPath = './test2-pddi.txt'
    jsonInput = './test2.json'
    rawFilePath = './test2.txt'

    mysqlSearch = databaseManager('root', 'karencita', 'rxnorm')

    with open(inputPath,'r') as inFile:
        with open(jsonInput, 'r') as jsonInputFile:
            with open(rawFilePath, 'r') as outFile:
                jsonObject = json.load(jsonInputFile)
                pddiResult = inFile.read()
                pddiLines = pddiResult.split('\n')
                outFileText = outFile.read()
                outFileLines = outFileText.split('\n')

                dictDrugsNames = {}
                complList = []
                missedElements = 0

                for element in jsonObject:
                    tempList = []
                    drugInText = outFileText[int(element['fro'])-1:int(element['to'])]
                    # print element

                    # getting the drug type
                    tempType = element['fullId']
                    fullIdElement = tempType.split('/')
                    drugType = fullIdElement[-2]
                    drugCUI = fullIdElement[-1]
                    # print drugType, drugCUI

                    if drugType == 'MSH':
                        if mysqlSearch.meshToRxnorm(drugCUI) != 0:
                            RXCUI = mysqlSearch.meshToRxnorm(drugCUI)
                        else:
                            RXCUI = '- MESHNOTFOUND' # for elements that cannot be mapped to rxnorm
                            missedElements += 1
                            # print 'MESHNOTFOUND'
                    else:
                        RXCUI = drugCUI

                    if RXCUI != '- MESHNOTFOUND':
                        # print RXCUI, 'added'
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', RXCUI)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', RXCUI)
                        currentResult = [RXCUI, conceptString, conceptType, drugInText, drugType, drugCUI, element['semTypes'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        key = drugInText #select the key that you want for the dictionary
                        if key in dictDrugsNames.keys():
                            dictDrugsNames[key].append(currentResult)
                        else:
                            dictDrugsNames[key] = [currentResult]

                # print dictDrugsNames

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
                        tempJsonObject['semtype'] = nestedelement[6]
                        tempJsonObject['to'] = nestedelement[7]
                        tempJsonObject['fro'] = nestedelement[8]
                        tempJsonObject['fullId'] = nestedelement[9]
                        tempJsonObject['preferredName'] = nestedelement[10]
                        # print tempJsonObject
                        extendedJson.append(tempJsonObject)

                normalizedJson = []
                for element in extendedJson:
                    tempJsonObject = {}

                    if element['rxConceptType']=='IN':
                        # print element['rxCui'], element['rxConcept'],' Ingredient'
                        key = element['mentionInText']
                        currentResult = [element['rxCui'], element['rxConcept'], element['rxConceptType'], element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['semtype'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)

                    elif element['rxConceptType']=='SCDC':
                        # print element['rxCui'], element['rxConcept'],'Semantic Clinical Dose Form Group '
                        nomrRxCui = mysqlSearch.getIngredient('ingredient_of', element['rxCui'])
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        currentResult = [nomrRxCui, conceptString, conceptType, element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['semtype'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        key = element['mentionInText']
                        tempJsonObject[key] = currentResult
                        normalizedJson.append(tempJsonObject)

                    elif element['rxConceptType']=='PIN':
                        # print element['rxCui'], element['rxConcept'],'Precise Ingredient'
                        # print mysqlSearch.getIngredient('has_form', element['rxCui'])
                        nomrRxCui = mysqlSearch.getIngredient('has_form', element['rxCui'])
                        conceptString = mysqlSearch.queryConcept('STR', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        conceptType = mysqlSearch.queryConcept('TTY', 'RXNCONSO', 'RXCUI', nomrRxCui)
                        currentResult = [nomrRxCui, conceptString, conceptType, element['mentionInText'], element['sourceTerm'], element['sourceCui'], element['semtype'], element['to'], element['fro'], element['fullId'], element['preferredName']]
                        tempJsonObject[nomrRxCui] = currentResult
                        normalizedJson.append(tempJsonObject)

                    ##FOR FUTURE USE INCLUDE OTHER RELATIONS
                    # elif element['rxConceptType']=='SBDG':
                    #     print element['rxCui'], element['rxConcept'],'Semantic Branded Dose Form Group'
                    #     print mysqlSearch.getIngredient('form_of', element['rxCui'])

                    # elif element['rxConceptType']=='DFG':
                    #     print element['rxCui'], element['rxConcept'],'Dose Form Group '
                    #     print mysqlSearch.getIngredient('form_of', element['rxCui'])

                    mappingToRxnorm = {}
                    for element in normalizedJson:
                        if element.keys() in mappingToRxnorm.keys():
                            if element.values()[0][0] != mappingToRxnorm[element.keys()]:
                                print 'rxcui inconsistence'
                        else:
                            mappingToRxnorm[element.keys()[0]]=element.values()[0][0]

                # print mappingToRxnorm

                logFile = open('log.txt','w')
                for listNorm in normalizedJson:
                    for key in listNorm:
                        print >>logFile,'1:','KEY:',key,'*** RXCUI ----->',listNorm[key][0]
                        print >>logFile,'2:','KEY:',key,'*** Concept from RXNORM ----->',listNorm[key][1]
                        print >>logFile,'3:','KEY:',key,'*** Concept Type ----->',listNorm[key][2]
                        print >>logFile,'4:','KEY:',key,'*** Drug mention in text ----->',listNorm[key][3]
                        print >>logFile,'5:','KEY:',key,'*** Source language ----->',listNorm[key][4]
                        print >>logFile,'6','KEY:',key,'*** CUI CODE in original terminology ----->',listNorm[key][5]
                        print >>logFile,'7:','KEY:',key,'*** Semantic type according to JSON Object ----->',listNorm[key][6]
                        print >>logFile,'8:','KEY:',key,'*** Final position in text according to JSON Object ----->',listNorm[key][7]
                        print >>logFile,'9:','KEY:',key,'*** Initial position according to JSON Object ----->',listNorm[key][8]
                        print >>logFile,'10:','KEY:',key,'*** Full ID according to JSON Object ----->',listNorm[key][9]
                        print >>logFile,'11:','KEY:',key,'*** Preferred name according to JSON Object ----->',listNorm[key][10]
                        print >>logFile,'---------------------------------------------------------'

                # for element in dictDrugsNames.keys():
                    # print element, dictDrugsNames[element]

                drugRetrieval = RxNormClient()
                dictDrugCuis = {}

                #Removing duplications - level 1: Using RxNorm Active Ingredients
                nlpPostProcessed_l1 = []

                totalInteractions = 0
                # print pddiLines
                for line in pddiLines:
                    totalInteractions += 1
                    interaction = line.split('\t')
                    if len(interaction)>1:
                        # print interaction
                        drugOne = interaction[0]
                        drugTwo = interaction[1]
                        print drugOne, 'vs.', drugTwo
                        print mappingToRxnorm[drugOne], ' vs.',mappingToRxnorm[drugTwo]
                        if mappingToRxnorm[drugOne] != mappingToRxnorm[drugTwo]:
                            nlpPostProcessed_l1.append(interaction)


    outFile = open('precessedNLP.txt','w')

    for line in nlpPostProcessed_l1:
        print >> outFile, "\t".join(line)

    print 'removed duplications', totalInteractions - len(nlpPostProcessed_l1)
    # print 'Normalized JSON Object:', len(normalizedJson), '\n', 'Original JSON Object:', len(jsonObject)
    print 'Number of missed JSON elements:', missedElements