/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivity.CheckConnectionInput;
import io.airbyte.workers.temporal.scheduling.shared.ActivityConfiguration;
import io.temporal.workflow.Workflow;

public class CheckConnectionWorkflowImpl implements CheckConnectionWorkflow {

  private final CheckConnectionActivity activity =
      Workflow.newActivityStub(CheckConnectionActivity.class, ActivityConfiguration.CHECK_ACTIVITY_OPTIONS);

  private static final String CHECK_JOB_OUTPUT_TAG = "check_job_output";
  private static final int CHECK_JOB_OUTPUT_TAG_CURRENT_VERSION = 1;

  @Override
  public ConnectorJobOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig launcherConfig,
                                final StandardCheckConnectionInput connectionConfiguration) {
    final CheckConnectionInput checkInput = new CheckConnectionInput(jobRunConfig, launcherConfig, connectionConfiguration);

    final int jobOutputVersion =
        Workflow.getVersion(CHECK_JOB_OUTPUT_TAG, Workflow.DEFAULT_VERSION, CHECK_JOB_OUTPUT_TAG_CURRENT_VERSION);

    if (jobOutputVersion < CHECK_JOB_OUTPUT_TAG_CURRENT_VERSION) {
      final StandardCheckConnectionOutput checkOutput = activity.run(checkInput);
      return new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION).withCheckConnection(checkOutput);
    }

    return activity.runWithJobOutput(checkInput);
  }

}
