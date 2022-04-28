/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

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
    if (meanByteSize <= 0.0) {
      return defaultFetchSize;
    }
    final long rawFetchSize = Math.round(bufferByteSize / meanByteSize);
    if (rawFetchSize > Integer.MAX_VALUE) {
      return maxFetchSize;
    }
    return Math.max(minFetchSize, Math.min(maxFetchSize, (int) rawFetchSize));
  }

  double getMeanRowByteSize() {
    return meanByteSize;
  }

}
