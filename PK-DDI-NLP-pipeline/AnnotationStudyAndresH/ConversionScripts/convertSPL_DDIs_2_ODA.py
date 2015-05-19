#!/usr/bin/python
#
# convertSPL_DDIs_2_ODA.py
#
# Export SPL DDI annotations to Open Data Annotation 

# Author: Richard Boyce and Andres Hernandez

# Copyright (C) 2012-2014 by Richard Boyce and the University of Pittsburgh
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
sys.path = sys.path + ['.']

import re, codecs, uuid, datetime
import os

## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON
import json

## import RDF related
from rdflib import Graph
from rdflib import BNode, Literal, Namespace, URIRef, RDF, RDFS

################################################################################
# CUSTOMIZABLE
################################################################################

# a CSV file containing the DDI extraction output after post
# processing to remove duplicates and assign the rxcuis for the drug
# mentions
inputData = '../pddi-postprocessed-output-performance.csv'

# path the original product label text
inputFileDir = '../input-files/'

# a CSV file containing the preferred name, exact string, and URIs of
# all drug mentions
drugListPath = 'NER-output.csv'

# the base URI to the SPLs when deployed in DOMEO
SPL_BASE_URI = 'http://130.49.206.86:8080/AnnoStudy/'

################################################################################
# NAMESPACE DECLARATIONS
################################################################################

poc = Namespace('http://purl.org/net/nlprepository/spl-ddi-annotation-poc#')             
dikbD2R = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/resource/')
dailymed = Namespace('http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')

dcterms = Namespace("http://purl.org/dc/terms/")
dctypes = Namespace("http://purl.org/dc/dcmitype/")
sio = Namespace('http://semanticscience.org/resource/')
oa = Namespace('http://www.w3.org/ns/oa#')
aoOld = Namespace('http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
cnt = Namespace('http://www.w3.org/2011/content#')
gcds = Namespace('http://www.genomic-cds.org/ont/genomic-cds.owl#')
ncit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
siocns = Namespace('http://rdfs.org/sioc/ns#')
swande = Namespace('http://purl.org/swan/1.2/discourse-elements#')
ncbit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')


############################################################ 
graph = Graph()

graph.namespace_manager.reset()
graph.namespace_manager.bind("dcterms", "http://purl.org/dc/terms/")
graph.namespace_manager.bind("pav", "http://purl.org/pav");
graph.namespace_manager.bind("dctypes", "http://purl.org/dc/dcmitype/")
graph.namespace_manager.bind('dailymed','http://dbmi-icode-01.dbmi.pitt.edu/linkedSPLs/vocab/resource/')
graph.namespace_manager.bind('sio', 'http://semanticscience.org/resource/')
graph.namespace_manager.bind('oa', 'http://www.w3.org/ns/oa#')
graph.namespace_manager.bind('aoOld', 'http://purl.org/ao/core/') # needed for AnnotationSet and item until the equivalent is in Open Data Annotation
graph.namespace_manager.bind('cnt', 'http://www.w3.org/2011/content#')
graph.namespace_manager.bind('gcds','http://www.genomic-cds.org/ont/genomic-cds.owl#')

graph.namespace_manager.bind('siocns','http://rdfs.org/sioc/ns#')
graph.namespace_manager.bind('swande','http://purl.org/swan/1.2/discourse-elements#')
graph.namespace_manager.bind('dikbD2R','http://dbmi-icode-01.dbmi.pitt.edu/dikb/vocab/resource/')

graph.namespace_manager.bind('poc','http://purl.org/net/nlprepository/spl-ddi-annotation-poc#')
graph.namespace_manager.bind('ncbit','http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
graph.namespace_manager.bind('ncit', 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')

### open annotation ontology properties and classes
graph.add((dctypes["Collection"], RDFS.label, Literal("Collection"))) # Used in lieau of the AnnotationSet https://code.google.com/p/annotation-ontology/wiki/AnnotationSet
graph.add((dctypes["Collection"], dcterms["description"], Literal("A collection is described as a group; its parts may also be separately described. See http://dublincore.org/documents/dcmi-type-vocabulary/#H7")))

graph.add((oa["Annotation"], RDFS.label, Literal("Annotation")))
graph.add((oa["Annotation"], dcterms["description"], Literal("Typically an Annotation has a single Body (oa:hasBody), which is the comment or other descriptive resource, and a single Target (oa:hasTarget) that the Body is somehow 'about'. The Body provides the information which is annotating the Target. See  http://www.w3.org/ns/oa#Annotation")))

graph.add((oa["annotatedBy"], RDFS.label, Literal("annotatedBy")))
graph.add((oa["annotatedBy"], RDF.type, oa["objectproperties"]))

graph.add((oa["annotatedAt"], RDFS.label, Literal("annotatedAt")))
graph.add((oa["annotatedAt"], RDF.type, oa["dataproperties"]))

graph.add((oa["TextQuoteSelector"], RDFS.label, Literal("TextQuoteSelector")))
graph.add((oa["TextQuoteSelector"], dcterms["description"], Literal("A Selector that describes a textual segment by means of quoting it, plus passages before or after it. See http://www.w3.org/ns/oa#TextQuoteSelector")))

graph.add((oa["hasSelector"], RDFS.label, Literal("hasSelector")))
graph.add((oa["hasSelector"], dcterms["description"], Literal("The relationship between a oa:SpecificResource and a oa:Selector. See http://www.w3.org/ns/oa#hasSelector")))

graph.add((oa["SpecificResource"], RDFS.label, Literal("SpecificResource")))
graph.add((oa["SpecificResource"], dcterms["description"], Literal("A resource identifies part of another Source resource, a particular representation of a resource, a resource with styling hints for renders, or any combination of these. See http://www.w3.org/ns/oa#SpecificResource")))

# these predicates are specific to SPL annotation
graph.add((sio["SIO_000628"], RDFS.label, Literal("refers to")))
graph.add((sio["SIO_000628"], dcterms["description"], Literal("refers to is a relation between one entity and the entity that it makes reference to.")))

graph.add((sio["SIO_000563"], RDFS.label, Literal("describes")))
graph.add((sio["SIO_000563"], dcterms["description"], Literal("describes is a relation between one entity and another entity that it provides a description (detailed account of)")))

graph.add((sio["SIO_000338"], RDFS.label, Literal("specifies")))
graph.add((sio["SIO_000338"], dcterms["description"], Literal("A relation between an information content entity and a product that it (directly/indirectly) specifies")))

graph.add((sio["SIO_000205"], RDFS.label, Literal("is represented by")))
graph.add((sio["SIO_000205"], dcterms["description"], Literal("is represented by: a relation between an entity and some symbol.")))

graph.add((sio["SIO_000062"], RDFS.label, Literal("is participant in")))
graph.add((sio["SIO_000062"], dcterms["description"], Literal("is participant in is a relation that describes the participation of the subject in the (processual) object.")))

graph.add((sio["SIO_000228"], RDFS.label, Literal("has role")))
graph.add((sio["SIO_000228"], dcterms["description"], Literal("has role is a relation between an entity and a role that it bears.")))


graph.add((sio["SIO_000132"], RDFS.label, Literal("has participant")))
graph.add((sio["SIO_000132"], dcterms["description"], Literal("has participant is a relation that describes the participation of the object in the (processual) subject.")))


## PD
graph.add((poc['PharmacodynamicImpact'], RDFS.label, Literal("PharmacodynamicImpact")))
graph.add((poc['PharmacodynamicImpact'], dcterms["description"], Literal("Information on the pharmacodynamic impact of a pharmacogenomic biomarker.")))

graph.add((poc['drug-toxicity-risk-increased'], RDFS.label, Literal("drug-toxicity-risk-increased")))
graph.add((poc['drug-toxicity-risk-increased'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increased risk of toxicity. ")))

graph.add((poc['drug-toxicity-risk-decreased'], RDFS.label, Literal("drug-toxicity-risk-decreased")))
graph.add((poc['drug-toxicity-risk-decreased'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an decreased risk of toxicity.")))

graph.add((poc['drug-efficacy-increased-from-baseline'], RDFS.label, Literal("drug-efficacy-increased-from-baseline")))
graph.add((poc['drug-efficacy-increased-from-baseline'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increase in the efficacy of the drug.")))

graph.add((poc['drug-efficacy-decreased-from-baseline'], RDFS.label, Literal("drug-efficacy-decreased-from-baseline")))
graph.add((poc['drug-efficacy-decreased-from-baseline'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in the efficacy of the drug")))

graph.add((poc['influences-drug-response'], RDFS.label, Literal("influences-drug-response")))
graph.add((poc['influences-drug-response'], dcterms["description"], Literal("The pharmacogenomic biomarker influences drug response")))

graph.add((poc['not-important'], RDFS.label, Literal("not-important")))
graph.add((poc['not-important'], dcterms["description"], Literal("The pharmacogenomic biomarker is not associated with a clinically relevant pharmacodynamic effect")))

## PK
graph.add((poc['PharmacokineticImpact'], RDFS.label, Literal("PharmacokineticImpact")))
graph.add((poc['PharmacokineticImpact'], dcterms["description"], Literal("Information on the pharmacokinetic impact of a pharmacogenomic biomarker.")))

graph.add((poc['absorption-increase'], RDFS.label, Literal("absorption-increase")))
graph.add((poc['absorption-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with an increase in absorption of the drug. ")))

graph.add((poc['absorption-decrease'], RDFS.label, Literal("absorption-decrease")))
graph.add((poc['absorption-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in absorption of the drug. ")))

graph.add((poc['distribution-increase'], RDFS.label, Literal("distribution-increase")))
graph.add((poc['distribution-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in distribution of the drug")))

graph.add((poc['distribution-decrease'], RDFS.label, Literal("distribution-decrease")))
graph.add((poc['distribution-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in distribution of the drug.")))

graph.add((poc['metabolism-increase'], RDFS.label, Literal("metabolism-increase")))
graph.add((poc['metabolism-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in metabolism of the drug")))

graph.add((poc['metabolism-decrease'], RDFS.label, Literal("metabolism-decrease")))
graph.add((poc['metabolism-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in metabolism of the drug.")))

graph.add((poc['excretion-increase'], RDFS.label, Literal("excretion-increase")))
graph.add((poc['excretion-increase'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a increase in excretion of the drug")))

graph.add((poc['excretion-decrease'], RDFS.label, Literal("excretion-decrease")))
graph.add((poc['excretion-decrease'], dcterms["description"], Literal("The pharmacogenomic biomarker is associated with a decrease in excretion of the drug ")))

graph.add((poc['not-important'], RDFS.label, Literal("not-important")))
graph.add((poc['not-important'], dcterms["description"], Literal("The pharmacogenomic biomarker is not associated any clinically relevant pharmacokinetic with respect to the drug. ")))

## Modality
graph.add((sio["SIO_001211"], RDFS.label, Literal("negative")))
graph.add((sio["SIO_001211"], dcterms["description"], Literal("negative is an assertional qualifier that expresses the falsity or lack of truth of a basic assertion.")))

graph.add((sio["SIO_001210"], RDFS.label, Literal("positive")))
graph.add((sio["SIO_001210"], dcterms["description"], Literal("positive is an assertional qualifier that expresses the validity or truth of a basic assertion.")))

## Statement
graph.add((ncit["qualitative"], RDFS.label, Literal("qualitative")))
graph.add((ncit["qualitative"], dcterms["description"], Literal("A measurement expressed in words rather than numbers.")))

graph.add((ncit["quantitative"], RDFS.label, Literal("quantitative")))
graph.add((ncit["quantitative"], dcterms["description"], Literal("Capable of being estimated or expressed with numeric values.")))

with open(drugListPath,'r') as drugList:
    drugListText = drugList.readlines()
    drugListObject = []

    for element in drugListText:
        line = element.strip()
        objectJson = line.split(';')
        drugListObject.append(objectJson)

with open(inputData,'r') as inFile:
    nlpAnnotations = inFile.readlines()
    i = 0 

    jsonOutput = []

    for annotation in nlpAnnotations[:]:
        jsonDictOutput = {}
        i += 1
        # print i
        ddiInfo = annotation.split('\t')
        label = ddiInfo[0]
        drugOne = ddiInfo[1]
        drugTwo = ddiInfo[2]
        initialSentence = ddiInfo[3]
        lenghtSentence = ddiInfo[4]
        modality = ddiInfo[6]
        sentence = ddiInfo[7]

        # Processing to get prefi and postfix
        inputFileText = inputFileDir + 'package-insert-section-' + str(label) + '.txt'

        with open(inputFileText, 'r') as drugLabel:
            drugLabelText = drugLabel.read()

            strippedDrugText = drugLabelText.strip()
            strippedSentence = sentence.strip()

            whiteSpacesLabel = re.finditer(" ", strippedDrugText)
            newLinesLabel = re.finditer(os.linesep, strippedDrugText)

            listSummary = []

            for space in whiteSpacesLabel:
                listSummary.append((space.span()[0],'sp'))

            for newLine in newLinesLabel:
                listSummary.append((newLine.span()[0],'nl'))

            deletedElements = sorted(listSummary, key=lambda match: match[0])

            lowerDrugText = strippedDrugText.lower()
            lowerSentence = strippedSentence.lower()

            trimmedDrugText = lowerDrugText.replace(" ", "")
            trimmedSentence = lowerSentence.replace(" ", "")

            nonlineDrugText = trimmedDrugText.replace(os.linesep, "")
            nonlineSentence = trimmedSentence.replace(os.linesep, "")
            
            indexStartSentence = nonlineDrugText.find(nonlineSentence)
            indexEndSentence = indexStartSentence+len(nonlineSentence)

            prefixText = nonlineDrugText[:indexStartSentence]
            intext = nonlineDrugText[indexStartSentence:indexEndSentence]
            postfixText = nonlineDrugText[indexEndSentence:]

             # '------------PREFIX------------------'
            templistPrefix = list(prefixText)
            count = 0 

            for spaceIndex in deletedElements:       
                if (spaceIndex[0]) > len(templistPrefix):
                    break
                elif spaceIndex[1] == 'sp':
                    templistPrefix.insert(spaceIndex[0], " ")
                elif spaceIndex[1] == 'nl':
                    templistPrefix.insert(spaceIndex[0], "\n")
                count += 1

            prefixTextSpaced = "".join(templistPrefix)

            if len(prefixTextSpaced) > 0:
                prefix = drugLabelText[0:len(prefixTextSpaced)]
            else:
                prefix = ""

            
             # '------------INTEXT------------------'
            tempListIntext = list(intext)

            for spaceIndex in deletedElements[count:]:      
                if (spaceIndex[0]-len(templistPrefix)) > len(tempListIntext):
                    break
                elif spaceIndex[1] == 'sp':
                    tempListIntext.insert(spaceIndex[0]-len(templistPrefix), " ")
                elif spaceIndex[1] == 'nl':
                    tempListIntext.insert(spaceIndex[0]-len(templistPrefix), "\n")

            inTextSpaced = "".join(tempListIntext)
            
            exact = drugLabelText[len(prefixTextSpaced):len(prefixTextSpaced)+len(inTextSpaced)]
            
             # '------------POSTFIX------------------'
            tempListPostFix = list(postfixText)

            for spaceIndex in deletedElements[count:]:      
                if (spaceIndex[0]-len(templistPrefix)-len(tempListIntext)) > len(tempListPostFix):
                    break
                elif spaceIndex[1] == 'sp':
                    tempListPostFix.insert(spaceIndex[0]-len(templistPrefix)-len(tempListIntext), " ")
                elif spaceIndex[1] == 'nl':
                    tempListPostFix.insert(spaceIndex[0]-len(templistPrefix)-len(tempListIntext), "\n")

            postfixSpaced = "".join(tempListPostFix)

            if len(postfixSpaced) > 0 :
                postfix = drugLabelText[len(prefixTextSpaced)+len(inTextSpaced):]
            else:
                postfix = ""

        # print "---------------------------------------------"
        # print "EXACT: %s" % exact
        # print "PRE: %s" % prefix
        # print "POST: %s" % postfix
        # print "---------------------------------------------"
        
        ## BUILD OA graph for each SPL
        splUri = SPL_BASE_URI + 'package-insert-section-' + str(label) + '.txt.html'
        currentAnnotSet = 'annotation-study-set-%s' % 'anno-study' + str(label) 
        currentAnnotItem = 'annotation-study-item-%s' % str(i) 

        graph.add((poc[currentAnnotSet], aoOld["item"], poc[currentAnnotItem])) # TODO: find out what is being used for items of collections in OA
        graph.add((poc[currentAnnotItem], RDF.type, oa["Annotation"]))
        graph.add((poc[currentAnnotItem], oa["annotatedAt"], Literal(datetime.date.today())))
        graph.add((poc[currentAnnotItem], oa["annotatedBy"], URIRef("http://www.pitt.edu/~rdb20/triads-lab.xml#TRIADS")))
        graph.add((poc[currentAnnotItem], oa["motivatedBy"], oa["tagging"]))

        currentAnnotItemUuid = URIRef("urn:uuid:%s" % uuid.uuid4())
        # currentAnnotItemUuid = URIRef(splUri)
        graph.add((poc[currentAnnotItem], oa["hasTarget"], currentAnnotItemUuid))
        
        graph.add((currentAnnotItemUuid, RDF.type, oa["SpecificResource"]))
        graph.add((currentAnnotItemUuid, RDF.type, poc["SPLConstrainedTarget"]))
        graph.add((currentAnnotItemUuid, oa["hasSource"], URIRef(splUri)))

        textConstraintUuid = URIRef("urn:uuid:%s" % uuid.uuid4())
        graph.add((currentAnnotItemUuid, oa["hasSelector"], textConstraintUuid))
        graph.add((textConstraintUuid, RDF.type, oa["TextQuoteSelector"]))

        #Get Prefix and postfix
        graph.add((textConstraintUuid, oa["exact"], Literal(exact)))
        graph.add((textConstraintUuid, oa["prefix"], Literal(prefix)))
        graph.add((textConstraintUuid, oa["postfix"], Literal(postfix))) 

        currentAnnotationBody = "annotation-study-body-%s" % str(i)
        graph.add((poc[currentAnnotItem], oa["hasBody"], poc[currentAnnotationBody]))


        #SIO Describes
        #Type of Data
        # graph.add((poc[currentAnnotationBody], sio["SIO_000205"], dikbD2R["Statement"]))  

        ## Modality
        if modality == 'negative':
            mod = "SIO_001211"
        elif modality == 'positive':
            mod = "SIO_001210"
        else:
            print 'not modality found'

        graph.add((poc[currentAnnotationBody], sio["SIO_000563"], dikbD2R["Modality"]))
        graph.add((poc[currentAnnotationBody], dikbD2R["Modality"], sio[mod]))

        currentDrug = []
        for drug in drugListObject:
            if label == drug[0]:
                currentDrug.append(drug)
        
        print currentDrug

        for drug in currentDrug:
            if drugOne == drug[2]:
                drugOneUri = drug[3]

        for drug in currentDrug:
            if drugTwo == drug[2]:
                drugTwoUri = drug[3]

        jsonDictOutput['label'] = label
        jsonDictOutput['prefix'] = prefix
        jsonDictOutput['exact'] = exact
        jsonDictOutput['suffix'] = postfix
        jsonDictOutput['modality'] = modality
        jsonDictOutput['modalityCui'] = mod
        jsonDictOutput['drugOneName'] = drugOne
        jsonDictOutput['drugTwoName'] = drugTwo
        jsonDictOutput['drugOneCui'] = drugOneUri
        jsonDictOutput['drugTwoCui'] = drugTwoUri

        # print drugOneUri, drugTwoUri

        # SIO refers to
        pk_ddi = URIRef("urn:uuid:%s" % uuid.uuid4())
        graph.add((poc[currentAnnotationBody], sio["SIO_000628"], pk_ddi))
        graph.add((pk_ddi, RDF.type, dikbD2R["PK_DDI"]))

        graph.add((pk_ddi, sio["SIO_000132"], poc['drug_entity']))
        graph.add((pk_ddi, poc['drug_entity'], URIRef(drugOneUri)))

        ## TODO: add back in if the object drug role is known
        # graph.add((poc['drug_entity'], sio["SIO_000228"], dikbD2R['ObjectDrugOfInteraction']))

        graph.add((pk_ddi, sio["SIO_000132"], poc['drug_entity'])) 
        graph.add((pk_ddi, poc['drug_entity'], URIRef(drugTwoUri)))
        
        ## TODO: add back in if the precipitant  drug role is known
        # graph.add((poc['drug_entity'], sio["SIO_000228"], dikbD2R['PrecipitantDrugOfInteraction']))

        jsonOutput.append(jsonDictOutput)
        

with open('jsonOutput.txt', 'w') as outfile:
  json.dump(jsonOutput, outfile)

# print graph.serialize(format="nt")
# print graph.serialize(format="xml")
print graph.serialize(format="json-ld")
