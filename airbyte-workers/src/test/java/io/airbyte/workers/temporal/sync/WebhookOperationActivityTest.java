/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.OperatorWebhookInput;
import io.airbyte.config.WebhookConfig;
import io.airbyte.config.WebhookOperationConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WebhookOperationActivityTest {

  private static final String WEBHOOK_EXECUTION_BODY = "fake-webhook-execution-body";
  private static final String WEBHOOK_EXECUTION_URL = "http://example.com";
  private WebhookOperationActivity webhookActivity;
  private HttpClient httpClient;
  private SecretsHydrator secretsHydrator;
  private static final UUID WEBHOOK_ID = UUID.randomUUID();
  private static final String WEBHOOK_AUTH_TOKEN = "fake-auth-token";
  private static final WebhookOperationConfigs WORKSPACE_WEBHOOK_CONFIGS = new WebhookOperationConfigs().withWebhookConfigs(List.of(
      new WebhookConfig().withId(WEBHOOK_ID).withAuthToken(WEBHOOK_AUTH_TOKEN)));

  @BeforeEach
  void init() {
    httpClient = mock(HttpClient.class);
    secretsHydrator = mock(SecretsHydrator.class);
    webhookActivity = new WebhookOperationActivityImpl(httpClient, secretsHydrator);
  }

  @Test
  void webhookActivityInvokesConfiguredWebhook() throws IOException, InterruptedException {
    final HttpResponse mockHttpResponse = mock(HttpResponse.class);
    when(mockHttpResponse.statusCode()).thenReturn(200).thenReturn(200);
    when(secretsHydrator.hydrate(any())).thenReturn(Jsons.jsonNode(WORKSPACE_WEBHOOK_CONFIGS));
    final OperatorWebhookInput input = new OperatorWebhookInput()
        .withExecutionBody(WEBHOOK_EXECUTION_BODY)
        .withExecutionUrl(WEBHOOK_EXECUTION_URL)
        .withWebhookConfigId(WEBHOOK_ID);
    // TODO(mfsiega-airbyte): make these matchers more specific.
    when(httpClient.send(any(), any())).thenReturn(mockHttpResponse);
    boolean success = webhookActivity.invokeWebhook(input);
    assertTrue(success);
  }

}
