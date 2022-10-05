/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.config.OperatorWebhookInput;
import io.airbyte.config.WebhookOperationConfig;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import javax.inject.Inject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class WebhookOperationActivityImpl implements WebhookOperationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebhookOperationActivityImpl.class);

  private final HttpClient client;

  @Inject
  private SecretsHydrator secretsHydrator;

  public WebhookOperationActivityImpl() {
    this.client = HttpClient.newHttpClient();
  }

  @Override
  public void invokeWebhook(OperatorWebhookInput input) {
    LOGGER.info("starting to invokeWebhook: {}", input);
    LOGGER.info("hydrating secrets: {}", input.getWebhookConfig());
    final JsonNode fullWebhookConfigJson =
        secretsHydrator.hydrate(new ObjectMapper().convertValue(input.getWebhookConfig(), JsonNode.class));
    LOGGER.info("hydrated: {}", fullWebhookConfigJson);
    final WebhookOperationConfig webhookConfig;
    try {
      webhookConfig = new ObjectMapper().treeToValue(fullWebhookConfigJson, WebhookOperationConfig.class);
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("about to send http request");
    final HttpRequest req = HttpRequest.newBuilder()
        .uri(URI.create(input.getExecutionUrl()))
        .POST(HttpRequest.BodyPublishers.ofString(input.getExecutionBody()))
        .header("Content-Type", "application/json")
        .header("Authorization", "Token " + webhookConfig.getAuthToken()).build();
    LOGGER.info(req.uri().toString());
    try {
      HttpResponse<String> response = this.client.send(req, HttpResponse.BodyHandlers.ofString());
      LOGGER.info(response.body());
    } catch (IOException | InterruptedException e) {
      throw new RuntimeException(e);
    } catch (Exception e) {
      LOGGER.debug(e.toString());
    }
  }

}
