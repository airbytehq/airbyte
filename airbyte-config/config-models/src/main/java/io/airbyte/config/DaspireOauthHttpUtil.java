

package io.airbyte.config;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

@Slf4j
public class DaspireOauthHttpUtil {

  private final static String GET_DASPIRE_OAUTH_CONFIG = "/oauth/config/get";
  private final static String WRITE_DASPIRE_OAUTH_CONFIG = "/oauth/config/save";

  public static String post(String uri, Map<String, Object> param) {
    log.error("post function URL ----> {}", uri);
    log.error("post function param ----> {}", param);
    CloseableHttpClient client = HttpClients.createDefault();
    try (client) {
      URIBuilder uriBuilder = new URIBuilder(uri);
      HttpPost httpPost = new HttpPost(uriBuilder.build());
      httpPost.setHeader("Content-type", "application/json; charset=utf-8");
      httpPost.setHeader("Accept", "application/json");
      ObjectMapper objectMapper = new ObjectMapper();
      String asString = objectMapper.writeValueAsString(param);
      StringEntity se = new StringEntity(asString, "utf-8");
      httpPost.setEntity(se);
      CloseableHttpResponse response = client.execute(httpPost);
      String res = EntityUtils.toString(response.getEntity(), "utf-8");
      response.close();
      return res;
    } catch (Exception e) {
      log.error("Rpc：msg:{}", e.getMessage());
    }
    return null;
  }

  public static JsonNode getDaspireOauthConfig(String workspaceId, String actorDefinitionId, String token) {
    try {
      Configs configs = new EnvConfigs();
      Map<String, Object> param = Map.of("workspaceId", workspaceId,
          "actorDefinitionId", actorDefinitionId,
          "token", token); 
      String jsonString = post(configs.getDaspireUrl() + GET_DASPIRE_OAUTH_CONFIG, param);
      log.error("static URL call :: start");
      String staticCallResponse = post("https://api-staging.daspire.com/daspire" + GET_DASPIRE_OAUTH_CONFIG, param);
      log.error("static URL call :: response -> {}", staticCallResponse);
      log.error("static URL call :: END");
      log.error("---------------------------------");
      log.error("static URL call with http :: start");
      String staticCallResponseHTTP = post("https://api-staging.daspire.com/daspire" + GET_DASPIRE_OAUTH_CONFIG, param);
      log.error("static URL call with http :: response -> {}", staticCallResponseHTTP);
      log.error("static URL call with http :: END");
      if (ObjectUtils.isNotEmpty(jsonString)) {
        JsonNode responseObject = new ObjectMapper().readTree(jsonString);
        if ("200".equals(responseObject.get("code").toString())) {
          return new ObjectMapper().readTree(responseObject.get("data").asText());
        }
      }
    } catch (JsonProcessingException e) {
      log.error("Rpc：msg:{}", e.getMessage());
    }
    return null;
  }

  public static Boolean writeDaspireOauthConfig(JsonNode config, String actorDefinitionId, String token) throws IOException {
    try {
      Configs configs = new EnvConfigs();
      Map<String, Object> param = Map.of(
          "config", config,
          "actorDefinitionId", actorDefinitionId,
          "token", token);
      String jsonString = post(configs.getDaspireUrl() + WRITE_DASPIRE_OAUTH_CONFIG, param);
      if (ObjectUtils.isNotEmpty(jsonString)) {
        JsonNode responseObject = new ObjectMapper().readTree(jsonString);
        if ("200".equals(responseObject.get("code").toString())) {
          log.info("Rpc：daspire config save successfully");
          return true;
        } else {
          log.error("Rpc：daspire response -> {}", responseObject);
        }
      }
    } catch (JsonProcessingException e) {
      log.error("Rpc：msg:{}", e.getMessage());
    }
    throw new IOException("Failed to write daspire data");
  }

}
