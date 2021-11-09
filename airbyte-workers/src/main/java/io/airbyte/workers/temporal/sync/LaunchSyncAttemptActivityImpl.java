/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.*;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;
import java.nio.file.Path;
import java.time.Duration;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LaunchSyncAttemptActivityImpl implements LaunchSyncAttemptActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(LaunchSyncAttemptActivityImpl.class);
  private static final String VERSION_LABEL = "sync-workflow";
  private static final int CURRENT_VERSION = 1;

  private static final int MAX_SYNC_TIMEOUT_DAYS = new EnvConfigs().getMaxSyncTimeoutDays();

  private static final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
      .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();

  private final ProcessFactory processFactory;

  public LaunchSyncAttemptActivityImpl(final ProcessFactory processFactory) {
    this.processFactory = processFactory;
  }

  @Override
  public StandardSyncOutput launch(JobRunConfig jobRunConfig,
                                   IntegrationLauncherConfig sourceLauncherConfig,
                                   IntegrationLauncherConfig destinationLauncherConfig,
                                   StandardSyncInput syncInput,
                                   UUID connectionId) {

    // for now keep same failure behavior where this is heartbeating and depends on the parent worker to exist
    final Process process = processFactory.create(
            "sync-attempt-" + UUID.randomUUID().toString().substring(0, 10),
            0,
            jobPath,
            imageName,
            false,
            fileMap,
            entrypoint,
            resourceRequirements,
            labels,
            args
    );

    // todo: handle exception
    process.waitFor();

    // todo: extract sync output from the job (maybe pull directly from persistence?)
    StandardSyncOutput run = null;

    return run;
  }

}
