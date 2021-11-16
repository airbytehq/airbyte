/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;

public interface DbtTransformationActivity {

  Void run(JobRunConfig jobRunConfig,
           IntegrationLauncherConfig destinationLauncherConfig,
           ResourceRequirements resourceRequirements,
           OperatorDbtInput input);

}
