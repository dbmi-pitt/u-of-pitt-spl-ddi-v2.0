package splPDDIExtractor;

import javax.jws.WebMethod;
import javax.jws.WebService;


@WebService(endpointInterface = "splPDDIExtractor.SPL_PDDI_NLP")
public interface SPL_PDDI_NLP_Interface {

    @WebMethod() 
	public String testPddi(String test, String rawtext, String drugs);
	
    @WebMethod() 
	public String sayHello(String name);
}
