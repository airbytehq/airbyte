import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import io.airbyte.integrations.base.Source;
import com.google.common.io.Resources;
import io.airbyte.protocol.models.AirbyteCatalog;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import com.fasterxml.jackson.databind.JsonNode;

import io.airbyte.protocol.models.ConnectorSpecification;

import io.airbyte.commons.json.Jsons;

public class SourceStockTicker extends Source{
	
	private HttpURLConnection con = null;
	
	//Read the spec.json file
	private String readResource(String name) throws IOException {
	    URL resource = Resources.getResource(name);		    
	    return Resources.toString(resource, StandardCharsets.UTF_8);
	}
	
	 //Step 1: Implement spec(), reads spec.json and print
	 public ConnectorSpecification spec() throws Exception {
		 String spec = readResource("spec.json");
		 System.out.println(spec);
		 //converting to ConnectorSpec object
		 return Jsons.deserialize(spec, ConnectorSpecification.class);
	 }
	 
	 //Step2 : implement check() and validate the url with api key generated from url.
	 public AirbyteConnectionStatus check(JsonNode config) {			
			//Invoke the url and populate status object;
			int responseCode = invokeurl(config);
			if (responseCode == HttpURLConnection.HTTP_OK) {
				return new AirbyteConnectionStatus().withStatus("SUCCEEDED");
			}
			else
				return new AirbyteConnectionStatus().withStatus("FAILED");
	 }
	 
	 //Step3 : implement discover() 
	 public AirbyteCatalog discover(JsonNode config) throws Exception {
		 List<AirByteStream> streams = new ArrayList<AirByteStream>();
		 String spec = readResource("catalog.json");
		 ObjectMapper mapper = new ObjectMapper();		 	
		 streams = objectMapper.readValue(streams, ArrayList.class);
		 return new AirbyteCatalog().withStreams(streams);		 	 
	 }
	 
	 
	 private int invokeurl(JsonNode config) {
		       URL obj = new URL("http://api.exchangeratesapi.io/v1/latest?access_key="+config.get("access_key"));	
				con = (HttpURLConnection) obj.openConnection();
				con.setRequestMethod("GET");
				//con.setRequestProperty("User-Agent", USER_AGENT);
				int responseCode = con.getResponseCode();
				return responseCode;
	 }
	 
	 public static void main(String[] args) {
		SourceStockTicker ticker = new SourceStockTicker();
		//test spec
		ConnectorSpecification config = ticker.spec();
		
		//read config file
		String validConfig = ticker.readResource("secrets/valid_config.json");
		ObjectMapper mapper = new ObjectMapper();
		JsonNode config = mapper.readTree(validConfig.toString());	
		//test check		
		ticker.check(config);
		
		
		//read config file
		String validConfig = ticker.readResource("secrets/invalid_config.json");
		ObjectMapper mapper = new ObjectMapper();
		JsonNode config = mapper.readTree(validConfig.toString());	
		//test check		
		ticker.check(config);
		
		//call discover()
		ticker.discover(config);
		
		
	}
}

