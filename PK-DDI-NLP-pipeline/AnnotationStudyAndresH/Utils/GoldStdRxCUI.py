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
    gsPath = './input-files/GoldStandardNER.txt'
    jsonInput = 'json-objects/GoldStandardNER.csv-PROCESSED.xml.json'

    mysqlSearch = databaseManager('amh211', 'annotationstudy', 'rxnorm')

    with open(gsPath,'r') as inFile:
        with open(jsonInput, 'r') as jsonInputFile:
            #gsFile = inFile.readlines()
            jsonObject = json.load(jsonInputFile)
            RawFile = inFile.read()

            dictDrugsNames = {}
            complList = []
            missedElements = 0

            for element in jsonObject:
                tempList = []
                drugInText = RawFile[int(element['fro'])-1:int(element['to'])]

                tempType = element['fullId']
                fullIdElement = tempType.split('/')
                drugType = fullIdElement[-2]
                drugCUI = fullIdElement[-1]

                if drugType == 'MSH':
                    if mysqlSearch.meshToRxnorm(drugCUI) != 0:
                        RXCUI = mysqlSearch.meshToRxnorm(drugCUI)
                    else:
                        RXCUI = '- MESHNOTFOUND' # for elements that cannot be mapped to rxnorm
                        missedElements += 1
                        print 'MESHNOTFOUND'
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
            # print dictDrugsNames.keys()

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
            # print extendedJson

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
            print mappingToRxnorm

    GDstandartINPUT = './goldStandardResults-performance.csv'
    GDstandartOUTPUT = './goldStandardResults-performance-CUI.csv'

    with open(GDstandartINPUT, 'r') as GSInput:
        with open(GDstandartOUTPUT, 'w') as GSOutput:
            GSInputFile = GSInput.readlines()

            fileOutList = []
            for line in GSInputFile:
                interaction = line.strip().split('\t')
                outline = list(interaction)
                # print interaction[2].strip(), interaction[7].strip()

                if interaction[2].strip() in mappingToRxnorm.keys():
                    outline.append(str(mappingToRxnorm[interaction[2].strip()]))

                if interaction[7].strip() in mappingToRxnorm.keys():
                    outline.append(str(mappingToRxnorm[interaction[7].strip()]))
                fileOutList.append(outline)
                print >> GSOutput, "\t".join(outline)

    print 'finished'