/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;

@ActivityInterface
public interface LaunchSyncAttemptActivity {

  @ActivityMethod
  StandardSyncOutput launch(final JobRunConfig jobRunConfig,
                            final IntegrationLauncherConfig sourceLauncherConfig,
                            final IntegrationLauncherConfig destinationLauncherConfig,
                            final StandardSyncInput syncInput,
                            final UUID connectionId);

}
