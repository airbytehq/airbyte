/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

@Slf4j
public class HttpUtil {

  private final static String DASPIRE_CONNECTION_COUNT = "/sync/connection/job/count";

  private final static String DASPIRE_CONNECTION_JOB_FAIL = "/sync/connection/job/fail";

  public static String post(String uri, Map<String, Object> param) {
    CloseableHttpClient client = HttpClients.createDefault();
    try (client) {
      log.info("RPC---------uri:{},pamra:{}", uri, param);
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
      log.info("Rpc：msg:{}", e.getMessage());
    }
    return null;
  }

  public static void daspireConnectionCount(Map<String, Object> param) {
    Configs configs = new EnvConfigs();
    log.info("config---------url:{},param:{}", configs.getDaspireUrl() + DASPIRE_CONNECTION_COUNT, param);
    post(configs.getDaspireUrl() + DASPIRE_CONNECTION_COUNT, param);
  }

  public static void jobFail(String workspaceId, String connectionName, String connectionId, String externalMessage, String failureOrigin) {
    Configs configs = new EnvConfigs();
    Map<String, Object> param = Map.of("workspaceId", workspaceId,
        "connectionName", connectionName,
        "connectionId", connectionId,
        "externalMessage", externalMessage,
        "failureOrigin", failureOrigin);
    log.info("config---------url:{},param:{}", configs.getDaspireUrl() + DASPIRE_CONNECTION_JOB_FAIL, param);
    post(configs.getDaspireUrl() + DASPIRE_CONNECTION_JOB_FAIL, param);
  }

}
