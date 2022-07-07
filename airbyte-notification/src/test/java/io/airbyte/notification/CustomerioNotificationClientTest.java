/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.notification;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;

import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.StandardWorkspace;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.Mockito;

class CustomerioNotificationClientTest {

  private static final String API_KEY = "api-key";
  private static final String URI_BASE = "https://customer.io";
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final StandardWorkspace WORKSPACE = new StandardWorkspace()
      .withWorkspaceId(WORKSPACE_ID)
      .withName("workspace-name")
      .withEmail("test@airbyte.io");
  private static final String RANDOM_INPUT = "input";

  @Mock
  private HttpClient mHttpClient;

  @BeforeEach
  void setUp() {
    mHttpClient = mock(HttpClient.class);
  }

  // this only tests that the headers are set correctly and that a http post request is sent to the
  // correct URI
  // this test does _not_ check the body of the request.
  @Test
  void notifyConnectionDisabled() throws IOException, InterruptedException {
    final CustomerioNotificationClient customerioNotificationClient = new CustomerioNotificationClient(new Notification()
        .withNotificationType(NotificationType.CUSTOMERIO), API_KEY, URI_BASE, mHttpClient);

    final HttpRequest expectedRequest = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(""))
        .uri(URI.create(URI_BASE))
        .header("Content-Type", "application/json")
        .header("Authorization", "Bearer " + API_KEY)
        .build();

    final HttpResponse httpResponse = mock(HttpResponse.class);
    Mockito.when(mHttpClient.send(Mockito.any(), Mockito.any())).thenReturn(httpResponse);
    Mockito.when(httpResponse.statusCode()).thenReturn(200);

    final boolean result =
        customerioNotificationClient.notifyConnectionDisabled(WORKSPACE.getEmail(), RANDOM_INPUT, RANDOM_INPUT, RANDOM_INPUT, WORKSPACE_ID,
            CONNECTION_ID);
    Mockito.verify(mHttpClient).send(expectedRequest, HttpResponse.BodyHandlers.ofString());

    assertTrue(result);
  }

}
