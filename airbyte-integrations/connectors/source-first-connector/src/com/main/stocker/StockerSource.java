/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package com.main.stocker;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.org.apache.xerces.internal.util.Status;

import io.airbyte.integrations.source.postgres.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;


public class StockerSource extends BaseConnector{

	
	@Override
	  public AirbyteConnectionStatus check(JsonNode config) {			
		//Invoke the url and populate status object;
		int responseCode = invokeurl(config);
		if (responseCode == HttpURLConnection.HTTP_OK) != null) {
			return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
		}
		else
			return new AirbyteConnectionStatus().withStatus(Status.FAILED);
	  }
 
	 private int invokeurl(JsonNode config) {
		 URL obj = new URL("http://api.exchangeratesapi.io/v1/latest?access_key="+config.get("access_key"));	
			HttpURLConnection con = (HttpURLConnection) obj.openConnection();
			con.setRequestMethod("GET");
			//con.setRequestProperty("User-Agent", USER_AGENT);
			int responseCode = con.getResponseCode();
			return responseCode;
	 }
	
	 @Override
	  public AirbyteCatalog discover(JsonNode config) throws Exception {
	    AirbyteCatalog catalog = super.discover(config);		 
	 }
 
	 @Override
	public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) {
		 URL obj = new URL("http://api.exchangeratesapi.io/v1/latest?access_key="+config.get("access_key"));	
			HttpURLConnection con = (HttpURLConnection) obj.openConnection();
			con.setRequestMethod("GET");
			//con.setRequestProperty("User-Agent", USER_AGENT);
			int responseCode = con.getResponseCode();
			JsonNode actualObj = null;
			System.out.println("GET Response Code :: " + responseCode);
			if (responseCode == HttpURLConnection.HTTP_OK) { // success
				BufferedReader in = new BufferedReader(new InputStreamReader(
						con.getInputStream()));
				String inputLine;
				StringBuffer response = new StringBuffer();
		
				while ((inputLine = in.readLine()) != null) {
					response.append(inputLine);
				}
				in.close();
		
				// print result
				System.out.println(response.toString());				
				ObjectMapper mapper = new ObjectMapper();
			    actualObj = mapper.readTree(response.toString());			   
			} else {
				System.out.println("GET request not worked");
			}
			 return super.read(config,catalog,actualObj);
	}
}