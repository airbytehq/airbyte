/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.WEBHOOK_CONFIG_ID_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.OperatorWebhookInput;
import io.airbyte.config.WebhookConfig;
import io.airbyte.config.WebhookOperationConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.metrics.lib.ApmTraceUtils;
import jakarta.inject.Singleton;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class WebhookOperationActivityImpl implements WebhookOperationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(WebhookOperationActivityImpl.class);
  private static final int MAX_RETRIES = 3;

  private final HttpClient httpClient;

  private final SecretsHydrator secretsHydrator;

  public WebhookOperationActivityImpl(final HttpClient httpClient, final SecretsHydrator secretsHydrator) {
    this.httpClient = httpClient;
    this.secretsHydrator = secretsHydrator;

  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public boolean invokeWebhook(final OperatorWebhookInput input) {
    LOGGER.debug("Webhook operation input: {}", input);
    LOGGER.debug("Found webhook config: {}", input.getWorkspaceWebhookConfigs());
    final JsonNode fullWebhookConfigJson = secretsHydrator.hydrate(input.getWorkspaceWebhookConfigs());
    final WebhookOperationConfigs webhookConfigs = Jsons.object(fullWebhookConfigJson, WebhookOperationConfigs.class);
    final Optional<WebhookConfig> webhookConfig =
        webhookConfigs.getWebhookConfigs().stream().filter((config) -> config.getId().equals(input.getWebhookConfigId())).findFirst();
    if (webhookConfig.isEmpty()) {
      throw new RuntimeException(String.format("Cannot find webhook config %s", input.getWebhookConfigId().toString()));
    }

    ApmTraceUtils.addTagsToTrace(Map.of(WEBHOOK_CONFIG_ID_KEY, input.getWebhookConfigId()));
    LOGGER.info("Invoking webhook operation {}", webhookConfig.get().getName());

    final HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
        .uri(URI.create(input.getExecutionUrl()));
    if (input.getExecutionBody() != null) {
      requestBuilder.POST(HttpRequest.BodyPublishers.ofString(input.getExecutionBody()));
    }
    if (webhookConfig.get().getAuthToken() != null) {
      requestBuilder
          .header("Content-Type", "application/json")
          .header("Authorization", "Bearer " + webhookConfig.get().getAuthToken()).build();
    }

    Exception finalException = null;
    // TODO(mfsiega-airbyte): replace this loop with retries configured on the HttpClient impl.
    for (int i = 0; i < MAX_RETRIES; i++) {
      try {
        final HttpResponse<String> response = this.httpClient.send(requestBuilder.build(), HttpResponse.BodyHandlers.ofString());
        LOGGER.debug("Webhook response: {}", response == null ? null : response.body());
        LOGGER.info("Webhook response status: {}", response == null ? "empty response" : response.statusCode());
        // Return true if the request was successful.
        final boolean isSuccessful = response != null && response.statusCode() >= 200 && response.statusCode() <= 300;
        LOGGER.info("Webhook {} execution status {}", webhookConfig.get().getName(), isSuccessful ? "successful" : "failed");
        return isSuccessful;
      } catch (final Exception e) {
        LOGGER.warn(e.getMessage());
        finalException = e;
      }
    }
    // If we ever get here, it means we exceeded MAX_RETRIES without returning in the happy path.
    throw new RuntimeException(finalException);
  }

}
