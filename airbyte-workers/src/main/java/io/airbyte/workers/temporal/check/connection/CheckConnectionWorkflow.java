/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface CheckConnectionWorkflow {

  @WorkflowMethod
  ConnectorJobOutput run(JobRunConfig jobRunConfig,
                         IntegrationLauncherConfig launcherConfig,
                         StandardCheckConnectionInput connectionConfiguration);

}
