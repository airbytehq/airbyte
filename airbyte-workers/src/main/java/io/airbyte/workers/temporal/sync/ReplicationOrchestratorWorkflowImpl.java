/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.UUID;

public class ReplicationOrchestratorWorkflowImpl implements ReplicationOrchestratorWorkflow {

  private static final int MAX_SYNC_TIMEOUT_DAYS = new EnvConfigs().getMaxSyncTimeoutDays();

  private static final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();

  private final ReplicationActivity replicationActivity = Workflow.newActivityStub(ReplicationActivity.class, options);

  @Override
  public StandardSyncOutput run(JobRunConfig jobRunConfig,
                                IntegrationLauncherConfig sourceLauncherConfig,
                                IntegrationLauncherConfig destinationLauncherConfig,
                                StandardSyncInput syncInput,
                                UUID connectionId) {
    return replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput, connectionId);
  }

}
