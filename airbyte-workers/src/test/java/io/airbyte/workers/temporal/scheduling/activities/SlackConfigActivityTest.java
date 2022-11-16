/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.Notification;
import io.airbyte.api.client.model.generated.NotificationType;
import io.airbyte.api.client.model.generated.SlackNotificationConfiguration;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.config.CustomerioNotificationConfiguration;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SlackConfigActivityTest {

  static private AirbyteApiClient mAirbyteApiClient;
  static private SlackConfigActivityImpl slackConfigActivity;

  @BeforeEach
  void setUp() {
    mAirbyteApiClient = mock(AirbyteApiClient.class, RETURNS_DEEP_STUBS);
    slackConfigActivity = new SlackConfigActivityImpl(mAirbyteApiClient);
  }

  @Test
  void testFetchSlackConfigurationSlackNotificationPresent() throws IOException, ApiException {
    UUID connectionId = UUID.randomUUID();
    ConnectionIdRequestBody requestBody = new ConnectionIdRequestBody().connectionId(connectionId);
    SlackNotificationConfiguration config = new SlackNotificationConfiguration().webhook("webhook");
    List<Notification> notifications = List.of(new Notification().notificationType(NotificationType.SLACK).slackConfiguration(config));
    final WorkspaceRead workspaceRead = new WorkspaceRead().workspaceId(UUID.randomUUID()).notifications(notifications);
    when(mAirbyteApiClient.getWorkspaceApi().getWorkspaceByConnectionId(requestBody)).thenReturn(workspaceRead);
    Assertions.assertThat("webhook").isEqualTo(slackConfigActivity.fetchSlackConfiguration(connectionId).get().getWebhook());
  }

  @Test
  void testFetchSlackConfigurationSlackNotificationNotPresent() throws IOException, ApiException {
    UUID connectionId = UUID.randomUUID();
    ConnectionIdRequestBody requestBody = new ConnectionIdRequestBody().connectionId(connectionId);
    CustomerioNotificationConfiguration config = new CustomerioNotificationConfiguration();
    List<Notification> notifications = List.of(new Notification().notificationType(NotificationType.CUSTOMERIO).customerioConfiguration(config));
    final WorkspaceRead workspaceRead = new WorkspaceRead().workspaceId(UUID.randomUUID()).notifications(notifications);
    when(mAirbyteApiClient.getWorkspaceApi().getWorkspaceByConnectionId(requestBody)).thenReturn(workspaceRead);
    Assertions.assertThat(Optional.ofNullable(null)).isEqualTo(slackConfigActivity.fetchSlackConfiguration(connectionId));
  }

}
