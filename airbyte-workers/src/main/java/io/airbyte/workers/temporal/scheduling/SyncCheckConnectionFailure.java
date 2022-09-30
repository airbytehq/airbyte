/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.helper.FailureHelper;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class SyncCheckConnectionFailure {

  private final Long jobId;
  private final Integer attemptId;
  private ConnectorJobOutput failureOutput;
  private FailureReason.FailureOrigin origin = null;

  public SyncCheckConnectionFailure(final JobRunConfig jobRunConfig) {
    Long jobId = 0L;
    Integer attemptId = 0;

    try {
      jobId = Long.valueOf(jobRunConfig.getJobId());
      attemptId = Math.toIntExact(jobRunConfig.getAttemptId());
    } catch (final Exception e) {
      // In tests, the jobId and attemptId may not be available
      log.warn("Cannot determine jobId or attemptId: " + e.getMessage());
    }

    this.jobId = jobId;
    this.attemptId = attemptId;
  }

  public boolean isFailed() {
    return this.origin != null && this.failureOutput != null;
  }

  public void setFailureOrigin(final FailureReason.FailureOrigin origin) {
    this.origin = origin;
  }

  public void setFailureOutput(final ConnectorJobOutput failureOutput) {
    this.failureOutput = failureOutput;
  }

  public StandardSyncOutput buildFailureOutput() {
    if (!this.isFailed()) {
      throw new RuntimeException("Cannot build failure output without a failure origin and output");
    }

    final StandardSyncOutput syncOutput = new StandardSyncOutput()
        .withStandardSyncSummary(
            new StandardSyncSummary()
                .withStatus(StandardSyncSummary.ReplicationStatus.FAILED)
                .withStartTime(System.currentTimeMillis())
                .withEndTime(System.currentTimeMillis())
                .withRecordsSynced(0L)
                .withBytesSynced(0L)
                .withTotalStats(new SyncStats()
                    .withRecordsEmitted(0L)
                    .withBytesEmitted(0L)
                    .withSourceStateMessagesEmitted(0L)
                    .withDestinationStateMessagesEmitted(0L)
                    .withRecordsCommitted(0L)));

    if (failureOutput.getFailureReason() != null) {
      syncOutput.setFailures(List.of(failureOutput.getFailureReason().withFailureOrigin(origin)));
    } else {
      final StandardCheckConnectionOutput checkOutput = failureOutput.getCheckConnection();
      final Exception ex = new IllegalArgumentException(checkOutput.getMessage());
      final FailureReason checkFailureReason = FailureHelper.checkFailure(ex, jobId, attemptId, origin);
      syncOutput.setFailures(List.of(checkFailureReason));
    }

    return syncOutput;
  }

  public static boolean isOutputFailed(final ConnectorJobOutput output) {
    if (output.getOutputType() != OutputType.CHECK_CONNECTION) {
      throw new IllegalArgumentException("Output type must be CHECK_CONNECTION");
    }

    return output.getFailureReason() != null || output.getCheckConnection().getStatus() == StandardCheckConnectionOutput.Status.FAILED;
  }

}
