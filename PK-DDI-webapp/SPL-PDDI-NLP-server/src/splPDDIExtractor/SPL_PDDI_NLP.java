package splPDDIExtractor;

import ddi.SPL_PK_DDI_NLP;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.ArrayList;

import javax.jws.WebService;

    @WebService(endpointInterface = "splPDDIExtractor.SPL_PDDI_NLP_Interface")
    public class SPL_PDDI_NLP implements SPL_PDDI_NLP_Interface {

	public String testPddi(String parser, String rawtext, String drugs){
	    SPL_PK_DDI_NLP pkDDI = new SPL_PK_DDI_NLP();

	    String[] drugArray = drugs.split(":");
	    System.out.println("INFO: passing drug list with " + drugArray.length + " items");

	    String outS = pkDDI.testClassifier(parser, rawtext, drugArray);

	    return outS;
	}

	public String sayHello(String name) {		    
	    return "Hello " + name;
	}

    }
