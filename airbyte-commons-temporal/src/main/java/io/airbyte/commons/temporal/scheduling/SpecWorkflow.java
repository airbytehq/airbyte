/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface SpecWorkflow {

  @WorkflowMethod
  ConnectorJobOutput run(JobRunConfig jobRunConfig, IntegrationLauncherConfig launcherConfig);

}
