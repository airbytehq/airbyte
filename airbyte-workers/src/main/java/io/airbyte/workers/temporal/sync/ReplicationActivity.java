/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface ReplicationActivity {

  @ActivityMethod
  StandardSyncOutput replicate(JobRunConfig jobRunConfig,
                               IntegrationLauncherConfig sourceLauncherConfig,
                               IntegrationLauncherConfig destinationLauncherConfig,
                               StandardSyncInput syncInput,
                               final String taskQueue);

}
