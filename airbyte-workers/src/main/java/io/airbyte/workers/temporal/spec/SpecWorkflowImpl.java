/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;

public class SpecWorkflowImpl implements SpecWorkflow {

  final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofHours(1))
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();
  private final SpecActivity activity = Workflow.newActivityStub(SpecActivity.class, options);

  @Override
  public ConnectorSpecification run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
    return activity.run(jobRunConfig, launcherConfig);
  }

}
