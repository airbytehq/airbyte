/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import java.util.List;
import java.util.UUID;

public class NormalizationTraceFailureSyncWorkflow implements SyncWorkflow {

  // Should match activity types from FailureHelper.java

  @VisibleForTesting
  public static final FailureReason FAILURE_REASON = new FailureReason()
      .withFailureOrigin(FailureOrigin.NORMALIZATION)
      .withTimestamp(System.currentTimeMillis());

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    return new StandardSyncOutput()
        .withNormalizationSummary(new NormalizationSummary()
            .withFailures(List.of(FAILURE_REASON))
            .withStartTime(System.currentTimeMillis() - 1000)
            .withEndTime(System.currentTimeMillis()));
  }

}
