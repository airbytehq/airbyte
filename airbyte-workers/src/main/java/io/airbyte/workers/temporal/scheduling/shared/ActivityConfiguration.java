/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.shared;

import io.airbyte.config.EnvConfigs;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityOptions;
import java.time.Duration;

/**
 * Shared temporal workflow configuration in order to ensure that
 * {@link io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow} and
 * {@link io.airbyte.workers.temporal.sync.SyncWorkflow} configurations are on sync, expecialy for
 * the grace period.
 */
public class ActivityConfiguration {

  private static final int MAX_SYNC_TIMEOUT_DAYS = new EnvConfigs().getSyncJobMaxTimeoutDays();

  public static final ActivityOptions OPTIONS = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();

}
