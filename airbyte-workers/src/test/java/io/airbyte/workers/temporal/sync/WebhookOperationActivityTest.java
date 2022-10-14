/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;

import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import java.net.http.HttpClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WebhookOperationActivityTest {

  private WebhookOperationActivity webhookActivity;
  private HttpClient httpClient;
  private SecretsHydrator secretsHydrator;

  @BeforeEach
  void init() {
    httpClient = mock(HttpClient.class);
    secretsHydrator = mock(SecretsHydrator.class);

    webhookActivity = new WebhookOperationActivityImpl(httpClient, secretsHydrator);
  }

  @Test
  void webhookAcitivtyIsNotNull() {
    assertNotNull(webhookActivity);
  }

}
