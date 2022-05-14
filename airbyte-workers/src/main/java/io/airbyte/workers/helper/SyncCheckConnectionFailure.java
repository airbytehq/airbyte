/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import io.airbyte.scheduler.models.JobRunConfig;
import java.util.List;

public class SyncCheckConnectionFailure {

  private final JobRunConfig jobRunConfig;
  private StandardCheckConnectionOutput failureOutput;
  private FailureReason.FailureOrigin origin = null;

  public SyncCheckConnectionFailure(JobRunConfig jobRunConfig) {
    this.jobRunConfig = jobRunConfig;
  }

  public boolean isFailed() {
    return this.origin != null && this.failureOutput != null;
  }

  public void setFailureOrigin(FailureReason.FailureOrigin origin) {
    this.origin = origin;
  }

  public void setFailureOutput(StandardCheckConnectionOutput failureOutput) {
    this.failureOutput = failureOutput;
  }

  public StandardSyncOutput buildFailureOutput() {
    if (!this.isFailed()) {
      throw new RuntimeException("Cannot build failure output without a failure origin and output");
    }

    final Exception ex = new IllegalArgumentException(failureOutput.getMessage());
    // TODO: Why are these values null and needing a default?
    final String jobId = jobRunConfig.getJobId() != null ? jobRunConfig.getJobId() : "1";
    final long attemptId = jobRunConfig.getAttemptId() != null ? jobRunConfig.getAttemptId() : 1L;
    final FailureReason checkFailureReason = FailureHelper.checkFailure(ex, Long.valueOf(jobId), Math.toIntExact(attemptId), origin);
    return new StandardSyncOutput()
        .withFailures(List.of(checkFailureReason))
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
                    .withStateMessagesEmitted(0L)
                    .withRecordsCommitted(0L)));
  }

}
