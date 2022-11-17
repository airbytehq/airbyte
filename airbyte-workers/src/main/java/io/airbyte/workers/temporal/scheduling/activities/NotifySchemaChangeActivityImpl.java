/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.notification.SlackNotificationClient;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.UUID;

@Singleton
public class NotifySchemaChangeActivityImpl implements NotifySchemaChangeActivity {

  @Override
  public boolean notifySchemaChange(SlackNotificationClient notificationClient, UUID connectionId, boolean isBreaking)
      throws IOException, InterruptedException {
    return notificationClient.notifySchemaChange(connectionId, isBreaking);
  }

}
