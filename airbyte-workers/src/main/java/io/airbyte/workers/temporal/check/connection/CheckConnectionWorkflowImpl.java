/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;

public class CheckConnectionWorkflowImpl implements CheckConnectionWorkflow {

  final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofHours(1))
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();
  private final CheckConnectionActivity activity = Workflow.newActivityStub(CheckConnectionActivity.class, options);

  @Override
  public StandardCheckConnectionOutput run(final JobRunConfig jobRunConfig,
                                           final IntegrationLauncherConfig launcherConfig,
                                           final StandardCheckConnectionInput connectionConfiguration) {
    return activity.run(jobRunConfig, launcherConfig, connectionConfiguration);
  }

}
