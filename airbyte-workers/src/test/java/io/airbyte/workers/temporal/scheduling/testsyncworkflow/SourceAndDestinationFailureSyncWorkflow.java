/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.SyncStats;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import java.util.Set;
import java.util.UUID;
import org.assertj.core.util.Sets;

public class SourceAndDestinationFailureSyncWorkflow implements SyncWorkflow {

  @VisibleForTesting
  public static final Set<FailureReason> FAILURE_REASONS = Sets.newLinkedHashSet(
      new FailureReason().withFailureOrigin(FailureOrigin.SOURCE).withTimestamp(System.currentTimeMillis()),
      new FailureReason().withFailureOrigin(FailureOrigin.DESTINATION).withTimestamp(System.currentTimeMillis()));

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    return new StandardSyncOutput()
        .withFailures(FAILURE_REASONS.stream().toList())
        .withStandardSyncSummary(new StandardSyncSummary()
            .withStatus(ReplicationStatus.FAILED)
            .withTotalStats(new SyncStats()
                .withRecordsCommitted(10L) // should lead to partialSuccess = true
                .withRecordsEmitted(20L)));
  }

}
