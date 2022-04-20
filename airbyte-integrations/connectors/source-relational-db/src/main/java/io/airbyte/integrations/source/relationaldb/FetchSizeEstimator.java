/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.google.common.annotations.VisibleForTesting;

/**
 * This class calculates how many rows to fetch in one batch in to prevent out-of-memory error. The
 * result is an estimation.
 */
public class FetchSizeEstimator {

  private long fetchBufferBytes = 200 * 1024 * 1024; // 200 MB
  private int defaultFetchSize = 1000;
  private int minFetchSize = 10;
  private int maxFetchSize = 100_000;

  private FetchSizeEstimator() {}

  @VisibleForTesting
  FetchSizeEstimator(final long fetchBufferBytes, final int minFetchSize, final int defaultFetchSize, final int maxFetchSize) {
    this.fetchBufferBytes = fetchBufferBytes;
    this.defaultFetchSize = defaultFetchSize;
    this.minFetchSize = minFetchSize;
    this.maxFetchSize = maxFetchSize;
  }

  public static FetchSizeEstimator getDefault() {
    return new FetchSizeEstimator();
  }

  public int getFetchSize(final long estimatedRowBytes) {
    if (estimatedRowBytes <= 0) {
      return defaultFetchSize;
    }
    final long rawFetchSize = fetchBufferBytes / estimatedRowBytes;
    return Math.min(maxFetchSize, Math.max(minFetchSize, (int) rawFetchSize));
  }

}
