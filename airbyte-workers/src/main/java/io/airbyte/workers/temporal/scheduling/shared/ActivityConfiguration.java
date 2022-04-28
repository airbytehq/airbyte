/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.shared;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import java.time.Duration;

/**
 * Shared temporal workflow configuration in order to ensure that
 * {@link io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow} and
 * {@link io.airbyte.workers.temporal.sync.SyncWorkflow} configurations are on sync, especially for
 * the grace period.
 */
public class ActivityConfiguration {

  private static final Configs configs = new EnvConfigs();

  private static final int MAX_SYNC_TIMEOUT_DAYS = configs.getSyncJobMaxTimeoutDays();
  private static final Duration DB_INTERACTION_TIMEOUT = Duration.ofSeconds(configs.getMaxActivityTimeoutSecond());

  // retry infinitely if the worker is killed without exceptions and dies due to timeouts
  // but fail for everything thrown by the call itself which is rethrown as runtime exceptions
  private static final RetryOptions ORCHESTRATOR_RETRY = RetryOptions.newBuilder()
      .setDoNotRetry(RuntimeException.class.getName(), WorkerException.class.getName())
      .build();

  private static final RetryOptions RETRY_POLICY = new EnvConfigs().getContainerOrchestratorEnabled() ? ORCHESTRATOR_RETRY : TemporalUtils.NO_RETRY;

  public static final ActivityOptions LONG_RUN_OPTIONS = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setStartToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setScheduleToStartTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(RETRY_POLICY)
      .setHeartbeatTimeout(TemporalUtils.HEARTBEAT_TIMEOUT)
      .build();

  public static final ActivityOptions CHECK_ACTIVITY_OPTIONS = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofMinutes(5))
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();

  public static final ActivityOptions SHORT_ACTIVITY_OPTIONS = ActivityOptions.newBuilder()
      .setStartToCloseTimeout(DB_INTERACTION_TIMEOUT)
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(TemporalUtils.RETRY)
      .setHeartbeatTimeout(TemporalUtils.HEARTBEAT_TIMEOUT)
      .build();

}
