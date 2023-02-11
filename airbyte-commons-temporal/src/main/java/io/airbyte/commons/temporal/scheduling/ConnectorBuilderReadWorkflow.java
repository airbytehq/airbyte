package io.airbyte.commons.temporal.scheduling;

import io.airbyte.config.ConnectorBuilderReadJobOutput;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface ConnectorBuilderReadWorkflow {

  @WorkflowMethod
  ConnectorJobOutput run(JobRunConfig jobRunConfig, StandardConnectorBuilderReadInput config);

}
