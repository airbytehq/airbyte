/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface NormalizationActivity {

  @ActivityMethod
  NormalizationSummary normalize(JobRunConfig jobRunConfig,
                                 IntegrationLauncherConfig destinationLauncherConfig,
                                 NormalizationInput input);

  @ActivityMethod
  NormalizationInput generateNormalizationInput(final StandardSyncInput syncInput, final StandardSyncOutput syncOutput);

}
