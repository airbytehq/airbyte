/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import java.util.Objects;

/**
 * POJO for all per-stream stats.
 * <p>
 * We are not able to use a {@link Record} since we want non-final fields to accumulate counts.
 */
public class StreamStats {

  public long estimatedRecords;
  public long estimatedBytes;
  public long emittedRecords;
  public long emittedBytes;

  public StreamStats() {
    this(0L, 0L, 0L, 0L);
  }

  public StreamStats(final long estimatedBytes, final long emittedBytes, final long estimatedRecords, final long emittedRecords) {
    this.estimatedRecords = estimatedRecords;
    this.estimatedBytes = estimatedBytes;
    this.emittedRecords = emittedRecords;
    this.emittedBytes = emittedBytes;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final StreamStats that = (StreamStats) o;
    return estimatedRecords == that.estimatedRecords && estimatedBytes == that.estimatedBytes && emittedRecords == that.emittedRecords
        && emittedBytes == that.emittedBytes;
  }

  @Override
  public int hashCode() {
    return Objects.hash(estimatedRecords, estimatedBytes, emittedRecords, emittedBytes);
  }

}
