/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.connector;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import io.airbyte.commons.temporal.scheduling.ConnectorBuilderReadWorkflow;
import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import java.util.Map;

public class ConnectorBuilderReadWorkflowImpl implements ConnectorBuilderReadWorkflow {

  @TemporalActivityStub(activityOptionsBeanName = "connectorBuilderReadActivityOptions")
  private ConnectorBuilderReadActivity activity;

  @Override
  public StandardConnectorBuilderReadOutput run(JobRunConfig jobRunConfig, StandardConnectorBuilderReadInput config) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, jobRunConfig.getAttemptId(), JOB_ID_KEY, jobRunConfig.getJobId(), DOCKER_IMAGE_KEY, "docker_image"));// FIXME
    return activity.run(jobRunConfig, config);
  }

}
