/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import java.util.ArrayList;
import java.util.UUID;

public class SyncWorkflowFailingOutputWorkflow implements SyncWorkflow {

  /**
   * Return an output that report a failure without throwing an exception. This failure is not a
   * partial success.
   */
  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {
    final StandardSyncSummary standardSyncSummary = new StandardSyncSummary()
        .withStatus(ReplicationStatus.FAILED)
        .withRecordsSynced(0L);

    final StandardSyncOutput standardSyncOutput = new StandardSyncOutput()
        .withStandardSyncSummary(standardSyncSummary)
        .withFailures(new ArrayList<>());

    return null;
  }

}
