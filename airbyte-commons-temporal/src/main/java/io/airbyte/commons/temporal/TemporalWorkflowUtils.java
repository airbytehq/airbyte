/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowClientOptions;
import io.temporal.client.WorkflowOptions;
import io.temporal.common.RetryOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import java.time.Duration;
import java.util.UUID;

/**
 * Collection of Temporal workflow related utility methods.
 *
 * <b>N.B</b>: These methods should not store any state or depend on any other objects/singletons
 * managed by the application framework.
 */
public class TemporalWorkflowUtils {

  public static final RetryOptions NO_RETRY = RetryOptions.newBuilder().setMaximumAttempts(1).build();

  private TemporalWorkflowUtils() {}

  public static ConnectionUpdaterInput buildStartWorkflowInput(final UUID connectionId) {
    return ConnectionUpdaterInput.builder()
        .connectionId(connectionId)
        .jobId(null)
        .attemptId(null)
        .fromFailure(false)
        .attemptNumber(1)
        .workflowState(null)
        .resetConnection(false)
        .fromJobResetFailure(false)
        .build();
  }

  public static WorkflowOptions buildWorkflowOptions(final TemporalJobType jobType, final String workflowId) {
    return WorkflowOptions.newBuilder()
        .setWorkflowId(workflowId)
        .setRetryOptions(NO_RETRY)
        .setTaskQueue(jobType.name())
        .build();
  }

  public static WorkflowOptions buildWorkflowOptions(final TemporalJobType jobType) {
    return WorkflowOptions.newBuilder()
        .setTaskQueue(jobType.name())
        .setWorkflowTaskTimeout(Duration.ofSeconds(27)) // TODO parker - temporarily increasing this to a recognizable number to see if it changes
        // error I'm seeing
        // todo (cgardens) we do not leverage Temporal retries.
        .setRetryOptions(RetryOptions.newBuilder().setMaximumAttempts(1).build())
        .build();
  }

  public static JobRunConfig createJobRunConfig(final UUID jobId, final int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(final long jobId, final int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(final String jobId, final int attemptId) {
    return new JobRunConfig()
        .withJobId(jobId)
        .withAttemptId((long) attemptId);
  }

  @VisibleForTesting
  public static WorkflowServiceStubsOptions getAirbyteTemporalOptions(final String temporalHost) {
    return WorkflowServiceStubsOptions.newBuilder()
        .setTarget(temporalHost)
        .build();
  }

  public static WorkflowClient createWorkflowClient(final WorkflowServiceStubs workflowServiceStubs, final String namespace) {
    return WorkflowClient.newInstance(
        workflowServiceStubs,
        WorkflowClientOptions.newBuilder()
            .setNamespace(namespace)
            .build());
  }

}
