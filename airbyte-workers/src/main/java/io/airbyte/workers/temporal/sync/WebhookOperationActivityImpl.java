/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.OperatorWebhookInput;
import io.airbyte.config.WebhookConfig;
import io.airbyte.config.WebhookOperationConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class WebhookOperationActivityImpl implements WebhookOperationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebhookOperationActivityImpl.class);

  private final HttpClient httpClient;

  private final SecretsHydrator secretsHydrator;

  public WebhookOperationActivityImpl(final HttpClient httpClient, final SecretsHydrator secretsHydrator) {
    this.httpClient = httpClient;
    this.secretsHydrator = secretsHydrator;

  }

  @Override
  public void invokeWebhook(OperatorWebhookInput input) {
    LOGGER.info("Invoking webhook operation {}", input.getName());
    final JsonNode fullWebhookConfigJson = secretsHydrator.hydrate(input.getWorkspaceWebhookConfigs());
    final WebhookOperationConfigs webhookConfigs = Jsons.object(fullWebhookConfigJson, WebhookOperationConfigs.class);

    final Optional<WebhookConfig> webhookConfig =
        webhookConfigs.getWebhookConfigs().stream().filter((config) -> config.getId() == input.getWebhookConfigId()).findFirst();
    if (!webhookConfig.isPresent()) {
      throw new RuntimeException(String.format("Can find webhook config %s", input.getWebhookConfigId().toString()));
    }

    final HttpRequest req = HttpRequest.newBuilder()
        .uri(URI.create(input.getExecutionUrl()))
        .POST(HttpRequest.BodyPublishers.ofString(input.getExecutionBody()))
        .header("Content-Type", "application/json")
        .header("Authorization", "Token " + webhookConfig.get().getAuthToken()).build();
    try {
      HttpResponse<String> response = this.httpClient.send(req, HttpResponse.BodyHandlers.ofString());
      LOGGER.debug("Webhook response: {}", response.body());
    } catch (IOException | InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

}
