/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.SlackNotificationConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.io.IOException;
import java.util.UUID;

@ActivityInterface
public interface NotifySchemaChangeActivity {

  @ActivityMethod
  public boolean notifySchemaChange(UUID connectionId, boolean isBreaking, SlackNotificationConfiguration config, String url)
      throws IOException, InterruptedException;

}
