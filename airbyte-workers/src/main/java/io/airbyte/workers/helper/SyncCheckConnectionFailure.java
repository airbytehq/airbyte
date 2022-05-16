/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import java.util.List;

public class SyncCheckConnectionFailure {

  private final Long jobId;
  private final Integer attemptId;
  private StandardCheckConnectionOutput failureOutput;
  private FailureReason.FailureOrigin origin = null;

  public SyncCheckConnectionFailure(Long jobId, Integer attemptId) {
    this.jobId = jobId;
    this.attemptId = attemptId;
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
    final FailureReason checkFailureReason = FailureHelper.checkFailure(ex, jobId, attemptId, origin);
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
