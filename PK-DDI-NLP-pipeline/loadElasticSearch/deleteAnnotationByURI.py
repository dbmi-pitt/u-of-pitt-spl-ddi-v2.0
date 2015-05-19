'''
Created 06/05/2014

@authors: Yifan Ning

@summary: clean DDI sets in COLLECTION of elasticsearch DB

'''

import MySQLdb, sys
import os
from elasticsearch import Elasticsearch
from subprocess import call

#LOCAL_IP = "130.49.206.86"
#PORT = "8080"
DB_CONFIG = "Domeo-DB-config.txt"

if len(sys.argv) > 3:
    COLLECTION = str(sys.argv[1])
    LOCAL_IP = str(sys.argv[2])
    PORT = str(sys.argv[3])
 
else:
	print "Usage: deleteAnnotationByURI <collection> <local ip> <port>"
	sys.exit(1)


def deleteAnnotationInMySQLAndElastico(annotates_url):

    dbconfig = file = open(DB_CONFIG)
    if dbconfig:
        for line in dbconfig:
            if "USERNAME" in line:
                DB_USER = line[(line.find("USERNAME=")+len("USERNAME=")):line.find(";")]
            elif "PASSWORD" in line:  
                DB_PWD = line[(line.find("PASSWORD=")+len("PASSWORD=")):line.find(";")]

        db = MySQLdb.connect(host= "localhost",
                  user= DB_USER,
                  passwd= DB_PWD,
                  db="DomeoAlphaDev")
    else:
        print "Mysql config file is not found: " + dbconfig

    cursor = db.cursor()

    try:
        # delete annotation in ES
        #sql0 = "SELECT mongo_uuid FROM annotation_set_index WHERE annotates_url ='" + annotates_url +"' and created_by_id != '" + USERID_NOTDELETE + "'"
        sql0 = "SELECT mongo_uuid FROM annotation_set_index WHERE annotates_url ='" + annotates_url +"'"
        #print sql0
        cursor.execute(sql0)
   
        results_mongo = cursor.fetchall()
        for row in results_mongo:
            deleteAnnotationInES(row[0])


        # get list of last_version_id to delete anns in annotation_set_permissions
        #sql1 = "SELECT id FROM annotation_set_index WHERE annotates_url ='" + annotates_url +"' and created_by_id != '" + USERID_NOTDELETE + "'"
        sql1 = "SELECT id FROM annotation_set_index WHERE annotates_url ='" + annotates_url +"'"
        version_id_list = []

        #print sql1
        cursor.execute(sql1)
    
        results_id = cursor.fetchall()
        for row in results_id:
            #print row
            version_id_list.append(row[0])
      


        for last_version_id in version_id_list:
            sql2 = "DELETE FROM annotation_set_permissions WHERE annotation_set_id ='" + last_version_id + "'"
            
            #print sql2
            cursor.execute(sql2)
            db.autocommit(True)
       
       
        #sql3 = "DELETE FROM annotation_set_index WHERE annotates_url = '" + annotates_url +"' and created_by_id != '" + USERID_NOTDELETE + "'"
        sql3 = "DELETE FROM annotation_set_index WHERE annotates_url = '" + annotates_url +"'"
        #print sql3
        cursor.execute(sql3)
        db.autocommit(True)

        # delete in last_annotation_set_index
        
        sql4 = "DELETE FROM last_annotation_set_index WHERE annotates_url = '" + annotates_url +"'"
        #print sql4
        cursor.execute(sql4)

        db.autocommit(True)
        db.close()
    except Exception, err:
        print "Exception, roll back"
        sys.stderr.write('ERROR: %s\n' % str(err))
        db.rollback()

def deleteAnnotationInES(mongo_uuid):
        #print mongo_uuid
        call(['curl' , '-XDELETE' , 'http://'+LOCAL_IP+':9200/domeo/'+COLLECTION+'/'+mongo_uuid])

        print "delete anno in ES"
	

# delete all of annotations that related to annotStudy

def clearAllAnnotations():
    
    # index = 0
    # #index = 21
    # while index<=208:
    #     URL = "http://"+LOCAL_IP + ":" + PORT +"/AnnoStudy/package-insert-section-"+str(index)+".txt.html"

    testSetIdL = ["44dcbf97-99ec-427c-ba50-207e0069d6d2", "39a5dae2-49f7-4662-9eac-aa7b4c7807a4","c66a11c1-3093-45ef-b348-3b196c05ba0c","50914a46-eab6-4c83-97cf-6ab0234c8126"]
    for setid in testSetIdL:
        URL = "http://130.49.206.86:" + PORT + "/proxy/http://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=" + setid
        deleteAnnotationInMySQLAndElastico(URL)
    
        print "delete annotation: " + URL
    call(['curl' , '-XDELETE' , 'http://'+LOCAL_IP+':9200/domeo/devb301/'])


# ----------------------main--------------------------------------

URL=""

def main():

    #deleteAnnotationInMySQL(URL)
    clearAllAnnotations()
    

if __name__ == "__main__":
    main()
