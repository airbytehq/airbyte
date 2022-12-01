/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.notification.SlackNotificationClient;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class NotifySchemaChangeActivityTest {

  static private SlackNotificationClient mNotificationClient;
  static private NotifySchemaChangeActivityImpl notifySchemaChangeActivity;

  @BeforeEach
  void setUp() {
    mNotificationClient = mock(SlackNotificationClient.class);
    notifySchemaChangeActivity = new NotifySchemaChangeActivityImpl();
  }

  @Test
  void testNotifySchemaChange() throws IOException, InterruptedException {
    UUID connectionId = UUID.randomUUID();
    boolean isBreaking = false;
    notifySchemaChangeActivity.notifySchemaChange(mNotificationClient, connectionId, isBreaking);
    verify(mNotificationClient, times(1)).notifySchemaChange(connectionId, isBreaking);
  }

}
