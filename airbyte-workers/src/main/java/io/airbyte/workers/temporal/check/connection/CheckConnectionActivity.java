/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
interface CheckConnectionActivity {

  @ActivityMethod
  StandardCheckConnectionOutput run(JobRunConfig jobRunConfig,
                                    IntegrationLauncherConfig launcherConfig,
                                    StandardCheckConnectionInput connectionConfiguration);

}
