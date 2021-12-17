/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface SpecWorkflow {

  @WorkflowMethod
  ConnectorSpecification run(JobRunConfig jobRunConfig, IntegrationLauncherConfig launcherConfig);

}
