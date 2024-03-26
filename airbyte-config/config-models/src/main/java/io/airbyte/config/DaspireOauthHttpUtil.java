/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

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

  public static String post(String uri, Map<String, Object> param) {
    log.error("DaspireOauthHttpUtil post function URL ----> {}", uri);
    log.error("DaspireOauthHttpUtil post function param ----> {}", param);
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

  public static JsonNode getDaspireOauthConfig(String workspaceId, String actorDefinitionId, String token) throws IOException {
    try {
      Configs configs = new EnvConfigs();
      Map<String, Object> param = Map.of("workspaceId", workspaceId,
          "actorDefinitionId", actorDefinitionId,
          "token", token);
      String jsonString = post(configs.getDaspireUrl() + GET_DASPIRE_OAUTH_CONFIG, param);

      if (ObjectUtils.isNotEmpty(jsonString)) {
        JsonNode responseObject = new ObjectMapper().readTree(jsonString);
        if ("200".equals(responseObject.get("code").toString())) {
          if (responseObject.get("data") != null && !responseObject.get("data").isNull()) {
            return new ObjectMapper().readTree(responseObject.get("data").asText());
          } else {
            return null;
          }
        } else {
          log.error("Daspire config API returns responses other than 200. responseObject :" + responseObject);
        }
      }
    } catch (JsonProcessingException e) {
      log.error("Rpc：msg:{}", e.getMessage());
    }
    throw new IOException("Failed to load Daspire OAuth Config");
  }

}
