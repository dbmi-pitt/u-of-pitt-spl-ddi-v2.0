__author__ = 'amh211'

from lxml import etree
import itertools
import json
import sys
import os.path

from XML2JSON.PDDI_NER_XMLparse import annotation, findAnnots

def findAnnotsDDI(tree):
    annots = []
    tree = etree.parse(filepath)
    top = tree.xpath('//annotatorResultBean')
    beans = tree.xpath('//annotationBean')

    for bean in beans:
        if len(bean.xpath('context/term/concept/fullId'))>0:
            fd = [bean.xpath('concept/fullId')[0].text.strip(),bean.xpath('context/term/concept/fullId')[0].text.strip()]
            nm = [bean.xpath('concept/preferredName')[0].text.strip(),bean.xpath('context/term/concept/preferredName')[0].text.strip()]
            to = bean.xpath('context/to')[0].text.strip()
            fro = bean.xpath('context/from')[0].text.strip()
            semList = [bean.xpath('concept/semanticTypes/semanticTypeBean/semanticType')[0].text.strip(),
            bean.xpath('context/term/concept/semanticTypes/semanticTypeBean/semanticType')[0].text.strip()]
            print fd, nm, to, fro, semList
            x = annotation(nm, fd, to, fro, semList)
            annots.append(x)
        else:
            continue
    return annots

if __name__=="__main__":
    filepath ='test6.xml'
    tree = etree.parse(filepath)
    listresults = findAnnotsDDI(tree)
    print len(listresults)




    # with open(filepath) as infile:
        # print infile.readlines()