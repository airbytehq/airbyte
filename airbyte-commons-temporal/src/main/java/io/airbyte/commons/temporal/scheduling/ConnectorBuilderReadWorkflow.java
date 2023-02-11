/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface ConnectorBuilderReadWorkflow {

  @WorkflowMethod
  StandardConnectorBuilderReadOutput run(JobRunConfig jobRunConfig, StandardConnectorBuilderReadInput config);

}
