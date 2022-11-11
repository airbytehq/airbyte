/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;

public class SpecWorkflowImpl implements SpecWorkflow {

  @TemporalActivityStub(activityOptionsBeanName = "specActivityOptions")
  private SpecActivity activity;

  @Override
  public ConnectorJobOutput run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
    return activity.run(jobRunConfig, launcherConfig);
  }

}
