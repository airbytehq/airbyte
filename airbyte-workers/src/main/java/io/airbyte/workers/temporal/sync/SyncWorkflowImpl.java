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
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.UUID;

public class SyncWorkflowImpl implements SyncWorkflow {

  private static final int MAX_SYNC_TIMEOUT_DAYS = new EnvConfigs().getMaxSyncTimeoutDays();

  private static final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();

  private static final ActivityOptions persistOptions = options.toBuilder()
      .setRetryOptions(RetryOptions.newBuilder()
          .setMaximumAttempts(10)
          .build())
      .build();

  // todo: remove PersistStateActivity in favor of in-workflow persistence

  private final LaunchSyncAttemptActivity launchSyncAttemptActivity = Workflow.newActivityStub(LaunchSyncAttemptActivity.class, persistOptions);

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    return launchSyncAttemptActivity.launch(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput, connectionId);
  }

}
