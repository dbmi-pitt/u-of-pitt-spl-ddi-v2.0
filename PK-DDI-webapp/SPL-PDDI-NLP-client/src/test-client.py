## test-client.py
#
# Test connectivity with the the SPL PK DDI NLP extractor service
#
# Author: Richard D Boyce
#
# 
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

import suds
 
WSDL_CACHE = False
PARSER = "clear"

class Client:
    def __init__(self):
        self.client = suds.client.Client("http://localhost:12341/splPDDIExtractor/SPL_PDDI_NLP?wsdl")
               
        if WSDL_CACHE:
            self.client.options.cache.setduration(days = 1)            
        else:
            self.client.set_options(cache = None)

        self.client.set_options(timeout = 900)

 
    def getHello(self):
        return self.client.service.sayHello("dude!")
 
    def testPDDI_NLP(self, rawText, drugS):
        return self.client.service.testPddi(PARSER, rawText, drugS)
     
if(__name__ == "__main__"):
    client = Client()
    print "INFO: connection test..."
    print client.getHello()

    print "INFO: PDDI extraction test..."
    rawText = "Concomitant use of paroxetine with risperidone, a CYP2D6 substrate has also been evaluated. In 1 study, daily dosing of paroxetine 20 mg in patients stabilized on risperidone (4 to 8 mg/day) increased mean plasma concentrations of risperidone approximately 4-fold, decreased 9-hydroxyrisperidone concentrations approximately 10%, and increased concentrations of the active moiety (the sum of risperidone plus 9-hydroxyrisperidone) approximately 1.4-fold."
    drugS = ["paroxetine:risperidone:9-hydroxyrisperidone"]
    nlpOut = client.testPDDI_NLP(rawText, drugS)
    print nlpOut
