/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.Notification;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.notification.SlackNotificationClient;
import java.io.IOException;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@Slf4j
class NotifySchemaChangeActivityTest {

  static private SlackNotificationClient mNotificationClient;
  static private NotifySchemaChangeActivityImpl notifySchemaChangeActivity;
  static private Notification mNotification;

  @BeforeEach
  void setUp() {
    mNotificationClient = mock(SlackNotificationClient.class);
    mNotification = mock(Notification.class);
    notifySchemaChangeActivity = spy(new NotifySchemaChangeActivityImpl());
  }

  @Test
  void testNotifySchemaChange() throws IOException, InterruptedException {
    UUID connectionId = UUID.randomUUID();
    String connectionUrl = "connection_url";
    boolean isBreaking = false;
    SlackNotificationConfiguration config = new SlackNotificationConfiguration();
    when(notifySchemaChangeActivity.createNotification(config)).thenReturn(mNotification);
    when(notifySchemaChangeActivity.createNotificationClient(mNotification)).thenReturn(mNotificationClient);
    notifySchemaChangeActivity.notifySchemaChange(connectionId, isBreaking, config, connectionUrl);
    verify(mNotificationClient, times(1)).notifySchemaChange(connectionId, isBreaking, config, connectionUrl);
  }

}
