/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import java.util.UUID;

public class SleepingSyncWorkflow implements SyncWorkflow {

  public static final Duration RUN_TIME = Duration.ofMinutes(10L);

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    Workflow.sleep(RUN_TIME);

    return new StandardSyncOutput();
  }

}
