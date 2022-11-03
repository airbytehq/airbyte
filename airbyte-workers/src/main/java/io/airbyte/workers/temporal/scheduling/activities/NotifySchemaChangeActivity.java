/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.notification.NotificationClient;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.io.IOException;
import java.util.UUID;

@ActivityInterface
public interface NotifySchemaChangeActivity {

  @ActivityMethod
  public boolean notifySchemaChange(NotificationClient notificationClient, UUID connectionId, boolean isBreaking)
      throws IOException, InterruptedException;

}
