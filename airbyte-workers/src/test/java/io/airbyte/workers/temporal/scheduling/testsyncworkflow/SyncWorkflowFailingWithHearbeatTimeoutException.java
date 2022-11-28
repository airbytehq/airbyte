/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.api.enums.v1.TimeoutType;
import io.temporal.failure.TimeoutFailure;
import io.temporal.workflow.Workflow;
import java.util.UUID;

/**
 * Test sync workflow to simulate a hearbeat timeout. It will:
 * <li>
 * <ol>
 * sleep for 10 minutes
 * </ol>
 * <ol>
 * throw a temporal timeout exception
 * </ol>
 * </li>
 */
public class SyncWorkflowFailingWithHearbeatTimeoutException implements SyncWorkflow {

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {
    Workflow.sleep(SleepingSyncWorkflow.RUN_TIME);
    throw new TimeoutFailure("heartbeat timeout", null, TimeoutType.TIMEOUT_TYPE_HEARTBEAT);
  }

}
