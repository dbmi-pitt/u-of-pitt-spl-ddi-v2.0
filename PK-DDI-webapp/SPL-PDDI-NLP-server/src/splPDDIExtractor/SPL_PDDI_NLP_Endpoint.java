package splPDDIExtractor;

import java.lang.String;

import javax.xml.ws.Endpoint;

import splPDDIExtractor.SPL_PDDI_NLP;

public class SPL_PDDI_NLP_Endpoint {
	
    public static void main(String[] args) {
		
	Endpoint.publish("http://localhost:12341/splPDDIExtractor/SPL_PDDI_NLP", new SPL_PDDI_NLP());
		
    }

}
