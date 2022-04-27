package io.airbyte.db.jdbc.streaming;

import io.airbyte.commons.json.Jsons;

public abstract class BaseSizeEstimator implements FetchSizeEstimator {

  private final long bufferByteSize;
  private final int minFetchSize;
  private final int defaultFetchSize;
  private final int maxFetchSize;

  protected double meanByteSize = 0.0;

  protected BaseSizeEstimator(final long bufferByteSize,
                              final int minFetchSize,
                              final int defaultFetchSize,
                              final int maxFetchSize) {
    this.bufferByteSize = bufferByteSize;
    this.minFetchSize = minFetchSize;
    this.defaultFetchSize = defaultFetchSize;
    this.maxFetchSize = maxFetchSize;
  }

  /**
   * Use serialized string size as an estimation of the byte size.
   */
  static long getEstimatedByteSize(final Object rowData) {
    if (rowData == null) {
      return 0L;
    }
    return Jsons.serialize(rowData).length() * 4L;
  }

  protected int getBoundedFetchSize() {
    if (meanByteSize <= 0L) {
      return defaultFetchSize;
    }
    final double rawFetchSize = bufferByteSize / meanByteSize;
    return Math.max(minFetchSize, Math.min(maxFetchSize, Double.valueOf(rawFetchSize).intValue()));
  }

  long getMeanRowByteSize() {
    return Double.valueOf(meanByteSize).longValue();
  }

}
