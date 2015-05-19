
#!/bin/bash

## pipeline.sh
#
# A script pipeline to run the SPL drug NER and PK PDDI NLP
#
# Authors: Richard D Boyce, Peter Randall, Andres Hernandez

## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Library General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or (at your option) any later version.

## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Library General Public License for more details.

## You should have received a copy of the GNU Library General Public
## License along with this library; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.

CURRENT_DATE=$(date +'%F%r' | tr -d ':' | tr -d 'PM' | tr -d 'AM')
DRUG_NER_BASEPATH=/home/PITT/rdb20/u-of-pitt-SPL-drug-NER
PDDI_CLIENT_PATH=/home/PITT/rdb20/u-of-pitt-spl-ddi-v2.0/PK-DDI-webapp/SPL-PDDI-NLP-client/src
PIPELINE_BASEPATH=/home/PITT/rdb20/u-of-pitt-spl-ddi-v2.0/PK-DDI-NLP-pipeline 
POST_PROCESSING_BASEPATH=/home/PITT/rdb20/u-of-pitt-spl-ddi-v2.0/PK-DDI-NLP-pipeline/AnnotationStudyAndresH

parse_to_JSON(){
    rm -f $POST_PROCESSING_BASEPATH/json-objects/*
    FILES=$DRUG_NER_BASEPATH/processed-output/*
    cd $PIPELINE_BASEPATH
    echo "INFO: parsing XML data to JSON, writing output to json-output..."
    for f in $FILES.xml; do 
	if [ -f $f ]; then
	    python $PIPELINE_BASEPATH/PDDI_NER_XMLparse.py $f
	fi
    done
    cp $PIPELINE_BASEPATH/json-output/* $POST_PROCESSING_BASEPATH/json-objects
    rm -f $PIPELINE_BASEPATH/json-output/*
    rm -f $DRUG_NER_BASEPATH/processed-output/*    
}

restart(){
    echo "INFO: restarting pipeline."
    echo "INFO: copying JSON NER data currently in ./json-NER-data to ./backup/json-NER-data."
    cp $PIPELINE_BASEPATH/json-output/* $PIPELINE_BASEPATH/backup/json-NER-data/
    zip -r json-NER-backup-${CURRENT_DATE}.zip $PIPELINE_BASEPATH/backup/json-NER-data/
     rm -f $PIPELINE_BASEPATH/backup/json-NER-data/*
    echo "INFO: copying JSON NER data in ${DRUG_NER_BASEPATH}/processed-output/ to ./json-output."
    parse_to_JSON
    echo "INFO: preparing restart..."
    python prepareRestart.py
}

get_spls(){
    echo "INFO: retrieving SPLS in setIds.txt from the SPARQL endpoint and writing to outfiles..."
    ##rm -f $PIPELINE_BASEPATH/outfiles/* 
    rm -rf $POST_PROCESSING_BASEPATH/tmp/infiles-for-NER/* 
    rm -rf $POST_PROCESSING_BASEPATH/tmp/infiles-for-NLP/*
    ## python retrieveSPLSquery.py
    cp $POST_PROCESSING_BASEPATH/input-files/* $POST_PROCESSING_BASEPATH/tmp/input-files-NER
 #   rm $POST_PROCESSING_BASEPATH/tmp/input-files-NER/TABLE*
    cp $POST_PROCESSING_BASEPATH/input-files/* $POST_PROCESSING_BASEPATH/tmp/input-files-NLP
 #   rm $POST_PROCESSING_BASEPATH/tmp/input-files-NLP/TABLE*

}

ner(){
    rm -rf $DRUG_NER_BASEPATH/textfiles/* 
    rm -rf $DRUG_NER_BASEPATH/processed-output/*
    #rm -f $POST_PROCESSING_BASEPATH/tmp/input-files-NER/*
    cp $POST_PROCESSING_BASEPATH/tmp/input-files-NER/* $DRUG_NER_BASEPATH/textfiles
    cd $DRUG_NER_BASEPATH
    echo "INFO: extracting drug entities from the SPL sections..."
    export CLASSPATH=$DRUG_NER_BASEPATH/lib/xml-apis-1.4.01.jar:$DRUG_NER_BASEPATH/lib/jena-iri-0.9.2.jar:$DRUG_NER_BASEPATH/lib/httpcore-4.1.3.jar:$DRUG_NER_BASEPATH/lib/extjwnl-1.6.4.jar:$DRUG_NER_BASEPATH/lib/commons-codec-1.5.jar:$DRUG_NER_BASEPATH/lib/jena-arq-2.9.2.jar:$DRUG_NER_BASEPATH/lib/log4j-1.2.16.jar:$DRUG_NER_BASEPATH/lib/commons-httpclient-3.0.1.jar:$DRUG_NER_BASEPATH/lib/commons-logging-1.1.1.jar:$DRUG_NER_BASEPATH/lib/concurrentlinkedhashmap-lru-1.2.jar:$DRUG_NER_BASEPATH/lib/jena-tdb-0.9.2.jar:$DRUG_NER_BASEPATH/lib/httpclient-4.1.2.jar:$DRUG_NER_BASEPATH/lib/extjwnl-utilities-1.6.4.jar:$DRUG_NER_BASEPATH/lib/jena-core-2.7.2.jar:$DRUG_NER_BASEPATH/lib/mysql-connector-java-5.1.17.jar:$DRUG_NER_BASEPATH/lib/xercesImpl-2.10.0.jar:$DRUG_NER_BASEPATH/lib/http-builder-0.5.2.jar:$DRUG_NER_BASEPATH/classes/:
    groovy $DRUG_NER_BASEPATH/src/groovy/util/PItoXML.groovy
    echo "INFO: output written to ${DRUG_NER_BASEPATH}/processed-output"
}

extract_PDDIs(){
    echo "INFO: running NLP to extract PDDIs. Output will be written to pddi-nlp-output..."
    #rm -f $PIPELINE_BASEPATH/pddi-nlp-output/*
    python /home/PITT/rdb20/u-of-pitt-spl-ddi-v2.0/PK-DDI-webapp/SPL-PDDI-NLP-client/src/splPDDINLPClient.py $POST_PROCESSING_BASEPATH/set-ids.txt $POST_PROCESSING_BASEPATH/tmp/input-files-NLP $POST_PROCESSING_BASEPATH/json-objects $POST_PROCESSING_BASEPATH/pddi-output 
    echo "INFO: NLP process completed"
}

post_processing(){
    echo "starting post-processing of the NLP results"
    # collects the files to be processed
    #ls $POST_PROCESSING_BASEPATH/pddi-output/ > postprocessed-ids.txt
    #find $POST_PROCESSING_BASEPATH/postprocessed-ids.txt -type f -exec sed -i "s/--PK-DDIs.txt//g" {} \;
    #cd $POST_PROCESSING_BASEPATH

    # identifying the active ingredient CUIs and removing duplicate drugs
    python ./PDDI-postprocessing.py

    # takes all of the files in the output folder and compiles them
    # into just one file with all of the DDI mentions
    python compileResults.py pddi-output
    python compileResults.py pddi-output-cui
    python compileResults.py pddi-postprocessed-output
    
    # removes duplication of the DDI mentions
    python SentenceCompiling.py pddi-output
    python SentenceCompiling.py pddi-output-cui
    python SentenceCompiling.py pddi-postprocessed-output

    # clean up file names
    find $POST_PROCESSING_BASEPATH/pddi-postprocessed-output-sentenceCompiled.csv -type f -exec sed -i "s/package-insert-section-//g" {} \;
    find $POST_PROCESSING_BASEPATH/pddi-postprocessed-output-sentenceCompiled.csv -type f -exec sed -i "s/--pddi-postprocessed.txt//g" {} \;

    find $POST_PROCESSING_BASEPATH/pddi-output-cui-sentenceCompiled.csv -type f -exec sed -i "s/package-insert-section-//g" {} \;
    find $POST_PROCESSING_BASEPATH/pddi-output-cui-sentenceCompiled.csv -type f -exec sed -i "s/--pddi-cui.txt//g" {} \;

    find $POST_PROCESSING_BASEPATH/pddi-output-sentenceCompiled.csv -type f -exec sed -i "s/package-insert-section-//g" {} \;
    find $POST_PROCESSING_BASEPATH/pddi-output-sentenceCompiled.csv -type f -exec sed -i "s/--PK-DDIs.txt//g" {} \;
    
    # adding the CUIs for the last columns in the CSV file. This file
    # creates the final version of the extracted PDDI dataset in a
    # file called "pddi-postprocessed-output-performance.csv"
    python completeCuis.py pddi-output
    python completeCuis.py pddi-postprocessed-output

    # checks performance against the reference standard DDI and NER
    # set. Expects PDDIs to be in
    # "pddi-postprocessed-output-performance.csv" and the Gold
    # standard annotation data to be in a file called
    # "goldStandardResults.csv"
    python computePerformance.py
}

#echo "Do you wish to restart the pipeline where it previously left off?"
#select yn in "Yes" "No"; do
#    case $yn in
#        Yes ) restart; break;;
#        No ) zip -r pddi-extraction-backup-$CURRENT_DATE.zip $PIPELINE_BASEPATH/json-output/* $PIPELINE_BASEPATH/outfiles/* $PIPELINE_BASEPATH/pddi-nlp-output/*; rm -f $PIPELINE_BASEPATH/outfiles/* $PIPELINE_BASEPATH/json-output/* $PIPELINE_BASEPATH/pddi-nlp-output/*; break;;
#    esac
#done

echo "Get ready to rumble!"
#   get_spls

#if [ "$(ls $POST_PROCESSING_BASEPATH/tmp/input-files-NER)" ]; then
#    ner
#    echo "NER finished"
#    ls $DRUG_NER_BASEPATH/processed-output
#   parse_to_JSON
    
#else
#   echo "INFO: skipping drug NER because outfiles is empty"
#fi

#if [ "$(ls $POST_PROCESSING_BASEPATH/json-objects)" ]; then
#    extract_PDDIs
#else
    #echo "INFO: skipping PDDI NLP because json-output is empty"
#fi

if [ "$(ls $POST_PROCESSING_BASEPATH/pddi-output)" ]; then
    post_processing
#else
#    echo "INFO: skipping PDDI NLP because json-output is empty"
fi

echo "INFO: Pipeline completed. Please check for errors or warnings."

exit 0
