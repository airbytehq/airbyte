/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface NormalizationActivity {

  @ActivityMethod
  NormalizationSummary normalize(JobRunConfig jobRunConfig,
                                 IntegrationLauncherConfig destinationLauncherConfig,
                                 NormalizationInput input);

}
