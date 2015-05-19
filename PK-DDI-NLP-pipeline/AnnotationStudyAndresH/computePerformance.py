__author__ = 'amh211'

if __name__=='__main__':
    drugOneGSIndex = 2
    drugTwoGSIndex = 7
    drugOneNLPIndex = 1
    drugTwoNLPIndex = 2

    drugOneGSIndexCUI = -2
    drugTwoGSIndexCUI = -1
    drugOneNLPIndexCUI = -2
    drugTwoNLPIndexCUI = -1

    with open('./goldStandardResults.csv','r') as goldStdFile:
        with open('./pddi-output-performance.csv', 'r') as nlpFile:
            with open('./pddi-postprocessed-output-performance.csv', 'r') as nlpPostFile:
                goldStd = goldStdFile.readlines()
                nlpRes = nlpFile.readlines()
                nlpPostRes = nlpPostFile.readlines()

                TPNLP = 0
                TOTALNLP = len(nlpRes)

                i = 0
                

                for goldinteraction in goldStd[0:]:
                    i += 1
                    j = 0

                    for nlpinteraction in nlpRes[0:]:
                        j += 1

                        if goldinteraction.split('\t')[0] == nlpinteraction.split('\t')[0]:
                            drugOneGS = goldinteraction.split('\t')[drugOneGSIndex].strip().lower()
                            drugTwoGS = goldinteraction.split('\t')[drugTwoGSIndex].strip().lower()
                            drugOneNLP = nlpinteraction.split('\t')[drugOneNLPIndex].strip().lower()
                            drugTwoNLP = nlpinteraction.split('\t')[drugTwoNLPIndex].strip().lower()

                            drugOneGSCUI = goldinteraction.split('\t')[drugOneGSIndexCUI].strip()
                            drugTwoGSCUI = goldinteraction.split('\t')[drugTwoGSIndexCUI].strip()
                            drugOneNLPCUI = nlpinteraction.split('\t')[drugOneNLPIndexCUI].strip()
                            drugTwoNLPCUI = nlpinteraction.split('\t')[drugTwoNLPIndexCUI].strip()

                            # if ((drugOneGSCUI == drugOneNLPCUI) and (drugTwoGSCUI == drugTwoNLPCUI) or ((drugOneGSCUI == drugTwoNLPCUI) and (drugTwoGSCUI == drugOneNLPCUI))):
                            if drugOneGSCUI and drugOneNLPCUI and drugTwoGSCUI and drugTwoNLPCUI:
                            	if ((drugOneGSCUI == drugOneNLPCUI) and (drugTwoGSCUI == drugTwoNLPCUI) or ((drugOneGSCUI == drugTwoNLPCUI) and (drugTwoGSCUI == drugOneNLPCUI))):
	                                if goldinteraction.split('\t')[12].strip().lower() == nlpinteraction.split('\t')[6].strip().lower():
	                                    TPNLP += 1
	                                    # print drugOneGSCUI, drugTwoGSCUI, drugOneNLPCUI, drugTwoNLPCUI
	                                    continue
                            elif ((drugOneGS == drugOneNLP) and (drugTwoGS == drugTwoNLP) or ((drugOneGS == drugTwoNLP) and (drugTwoGS == drugOneNLP))):
                                if goldinteraction.split('\t')[12].strip().lower() == nlpinteraction.split('\t')[6].strip().lower():
                                    TPNLP += 1
                                    # print drugOneGS, drugTwoGS, drugOneNLP, drugTwoNLP
                                    continue
                            

                

                print 'total nlp',j
    
                FPNLP = TOTALNLP - TPNLP

                TPPOSTNLP = 0
                TOTALNLP = len(nlpPostRes)

                for goldinteraction in goldStd[0:]:
                    j = 0
                    for nlpinteraction in nlpPostRes[0:]:
                        j += 1
                        if goldinteraction.split('\t')[0] == nlpinteraction.split('\t')[0]:
                            drugOneGS = goldinteraction.split('\t')[drugOneGSIndex].strip().lower()
                            drugTwoGS = goldinteraction.split('\t')[drugTwoGSIndex].strip().lower()
                            drugOneNLP = nlpinteraction.split('\t')[drugOneNLPIndex].strip().lower()
                            drugTwoNLP = nlpinteraction.split('\t')[drugTwoNLPIndex].strip().lower()
                            # print drugOneGS, drugTwoGS, drugOneNLP, drugTwoNLP

                            drugOneGSCUI = goldinteraction.split('\t')[drugOneGSIndexCUI].strip()
                            drugTwoGSCUI = goldinteraction.split('\t')[drugTwoGSIndexCUI].strip()
                            drugOneNLPCUI = nlpinteraction.split('\t')[drugOneNLPIndexCUI].strip()
                            drugTwoNLPCUI = nlpinteraction.split('\t')[drugTwoNLPIndexCUI].strip()

                            # if ((drugOneGSCUI == drugOneNLPCUI) and (drugTwoGSCUI == drugTwoNLPCUI) or ((drugOneGSCUI == drugTwoNLPCUI) and (drugTwoGSCUI == drugOneNLPCUI))):
                            if drugOneGSCUI and drugOneNLPCUI and drugTwoGSCUI and drugTwoNLPCUI:
	                            if ((drugOneGSCUI == drugOneNLPCUI) and (drugTwoGSCUI == drugTwoNLPCUI) or ((drugOneGSCUI == drugTwoNLPCUI) and (drugTwoGSCUI == drugOneNLPCUI))):
	                                if goldinteraction.split('\t')[12].strip().lower() == nlpinteraction.split('\t')[6].strip().lower():
	                                    TPPOSTNLP += 1
	                                    # print drugOneGSCUI, drugTwoGSCUI, drugOneNLPCUI, drugTwoNLPCUI
	                                    continue
                            elif ((drugOneGS == drugOneNLP) and (drugTwoGS == drugTwoNLP) or ((drugOneGS == drugTwoNLP) and (drugTwoGS == drugOneNLP))):
                                if goldinteraction.split('\t')[12].strip().lower() == nlpinteraction.split('\t')[6].strip().lower():
                                    TPPOSTNLP += 1
                                    continue
                            
                print 'total post-NLP', j
                FPPOSTNLP = TOTALNLP - TPPOSTNLP

                labelsNLP = []
                for nlpinteraction in nlpRes[0:]:
                    labelsNLP.append(nlpinteraction.split('\t')[0])
                setLabelsNLP = sorted(set(labelsNLP))

                TOTALGSNLP = 0
                for element in goldStd[0:]:
                    if element.split('\t')[0] in setLabelsNLP:
                        TOTALGSNLP += 1

                FNNLP = TOTALGSNLP - TPNLP
                print 'Total interactions in NLP: ', TOTALGSNLP, 'of', i

                labelsPostNLP = []
                for nlpinteraction in nlpPostRes[0:]:
                    labelsPostNLP.append(nlpinteraction.split('\t')[0])
                setLabelsPostNLP = sorted(set(labelsPostNLP))

                TOTALGSPOSTNLP = 0
                for element in goldStd[0:]:
                    if element.split('\t')[0] in setLabelsPostNLP:
                        TOTALGSPOSTNLP += 1

                FNPOSTNLP = TOTALGSPOSTNLP - TPPOSTNLP
                print 'Total interactions in Post-NLP: ', TOTALGSPOSTNLP, 'of', i

                PRECISIONNLP = round(float(TPNLP)/float(TPNLP+FPNLP),4)
                RECALLNLP = round(float(TPNLP)/float(TPNLP+FNNLP),4)
                FNLP = 2 * (PRECISIONNLP * RECALLNLP)/(PRECISIONNLP+RECALLNLP)
                PRECISIONPOSTNLP = round(float(TPPOSTNLP)/float(TPPOSTNLP+FPPOSTNLP),4)
                RECALLPOSTNLP = round(float(TPPOSTNLP)/float(TPPOSTNLP+FNPOSTNLP),4)
                FPOSTNLP = 2 * (PRECISIONPOSTNLP * RECALLPOSTNLP)/(PRECISIONPOSTNLP+RECALLPOSTNLP)

                print '----------------------------------------------'
                print 'true positive NLP:', TPNLP
                print 'false positive NLP:', FPNLP
                print 'false negative NLP:', FNNLP
                print 'precision NLP', PRECISIONNLP
                print 'RecallNLP NLP', RECALLNLP
                print 'f-measure NLP', FNLP
                print '----------------------------------------------'
                print 'true positive PostNLP:', TPPOSTNLP
                print 'false positive PostNLP:', FPPOSTNLP
                print 'false negative PostNLP:', FNPOSTNLP
                print 'precision NLP', PRECISIONPOSTNLP
                print 'RecallNLP NLP', RECALLPOSTNLP
                print 'f-measure NLP', FPOSTNLP
                print '----------------------------------------------'

    print 'finished'
