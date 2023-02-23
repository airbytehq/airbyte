/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import java.util.List;

public class SyncOutputProvider {

  public final static StandardSyncSummary EMPTY_FAILED_SYNC = new StandardSyncSummary()
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
          .withRecordsCommitted(0L));

  public static StandardSyncOutput getRefreshSchemaFailure(final Exception e) {
    return new StandardSyncOutput()
        .withFailures(List.of(new FailureReason()
            .withFailureType(FailureReason.FailureType.REFRESH_SCHEMA)
            .withFailureOrigin(FailureReason.FailureOrigin.SOURCE)
            .withExternalMessage("Failed to detect if there is a schema change. If the error persist please contact the support team.")
            .withInternalMessage("Failed to launch the refresh schema activity because of: " + e.getMessage())
            .withStacktrace(e.toString())))
        .withStandardSyncSummary(EMPTY_FAILED_SYNC);
  }

}
