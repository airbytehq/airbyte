/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.workflow.Workflow;

public class CheckConnectionWorkflowImpl implements CheckConnectionWorkflow {
  private final CheckConnectionActivity activity =
      Workflow.newActivityStub(CheckConnectionActivity.class, ActivityConfiguration.CHECK_ACTIVITY_OPTIONS);

  @Override
  public StandardCheckConnectionOutput run(final JobRunConfig jobRunConfig,
                                           final IntegrationLauncherConfig launcherConfig,
                                           final StandardCheckConnectionInput connectionConfiguration) {

    return activity.check(jobRunConfig, launcherConfig, connectionConfiguration);
  }

}
