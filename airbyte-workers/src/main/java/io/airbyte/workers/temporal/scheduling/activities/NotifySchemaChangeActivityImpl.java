/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.notification.NotificationClient;
import java.io.IOException;
import java.util.UUID;

public class NotifySchemaChangeActivityImpl implements NotifySchemaChangeActivity {

  public boolean notifySchemaChange(NotificationClient notificationClient, UUID connectionId, boolean isBreaking)
      throws IOException, InterruptedException {
    return notificationClient.notifySchemaChange(connectionId, isBreaking);
  }

}
