/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DbtCloudClientImpl implements DbtCloudClient {

  private final String accountId;
  private final String token;
  private final HttpClient client;

  public DbtCloudClientImpl(final String accountId, final String token) {
    this.accountId = accountId;
    this.token = token;
    this.client = HttpClient.newHttpClient();
  }

  @Override
  public String triggerRun(final String jobId) {
    final HttpRequest req = HttpRequest.newBuilder()
        .uri(URI.create(String.format("https://cloud.getdbt.com/api/v2/accounts/%s/jobs/%s/run/", this.accountId, jobId)))
        .POST(HttpRequest.BodyPublishers.ofString("{\"cause\": \"Airbyte connection\"}"))
        .header("Content-Type", "application/json")
        .header("Authorization", "Token " + this.token).build();
    log.info(req.uri().toString());
    try {
      HttpResponse<String> response = this.client.send(req, HttpResponse.BodyHandlers.ofString());
      ObjectMapper mapper = new ObjectMapper();
      Map<String, Object> result = mapper.convertValue(Jsons.deserialize(response.body()), new TypeReference<Map<String, Object>>() {});
      log.info(response.body());
      return (String) result.get("data").toString();
    } catch (IOException | InterruptedException e) {
      throw new RuntimeException(e);
    } catch (Exception e) {
      log.debug(e.toString());
      return "";
    }
  }

}
