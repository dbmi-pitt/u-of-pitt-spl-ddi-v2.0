__author__ = 'amh211'

import json
import urllib2
import urllib
import traceback
import sys

def query(q,apikey,epr,f='application/json'):
    """Function that uses urllib/urllib2 to issue a SPARQL query.
       By default it requests json as data format for the SPARQL resultset"""

    try:
        params = {'query': q, 'apikey': apikey}
        params = urllib.urlencode(params)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr+'?'+params)
        request.add_header('Accept', f)
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e

if __name__ == "__main__":
    sparql_service = "http://alphasparql.bioontology.org/sparql/"

    #To get your API key register at http://bioportal.bioontology.org/accounts/new
    api_key = "f3c4374a-e69f-4a13-bc28-7f5a78e244ee"

    #Some sample query.
    query_string = """
PREFIX omv: <http://omv.ontoware.org/2005/05/ontology#>

SELECT ?ont ?name ?acr
WHERE { ?ont a omv:Ontology;
             omv:acronym ?acr;
             omv:name ?name .
}
"""
    json_string = query(query_string, api_key, sparql_service)
    resultset=json.loads(json_string)

    #Printing the json object.
    print json.dumps(resultset,indent=1)