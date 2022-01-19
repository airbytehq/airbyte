/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface SpecActivity {

  @ActivityMethod
  ConnectorSpecification run(JobRunConfig jobRunConfig, IntegrationLauncherConfig launcherConfig);

}
