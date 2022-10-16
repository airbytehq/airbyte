/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface DbtTransformationActivity {

  @ActivityMethod
  Void run(JobRunConfig jobRunConfig,
           IntegrationLauncherConfig destinationLauncherConfig,
           ResourceRequirements resourceRequirements,
           OperatorDbtInput input);

}
