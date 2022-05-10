/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.util.Optional;

/**
 * This class estimates the mean row byte size by measuring the first consecutive
 * {@code initialSampleSize} rows.
 */
public class InitialSizeEstimator extends BaseSizeEstimator implements FetchSizeEstimator {

  private final int sampleSize;
  private int counter = 0;

  public InitialSizeEstimator(final long bufferByteSize,
                              final int initialSampleSize,
                              final int minFetchSize,
                              final int defaultFetchSize,
                              final int maxFetchSize) {
    super(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize);
    this.sampleSize = initialSampleSize;
  }

  @Override
  public void accept(final Object row) {
    final long byteSize = getEstimatedByteSize(row);
    // divide each byteSize by sampleSize to prevent overflow
    meanByteSize += 1.0 * byteSize / sampleSize;
    counter++;
  }

  @Override
  public Optional<Integer> getFetchSize() {
    if (counter < sampleSize) {
      return Optional.empty();
    }
    return Optional.of(getBoundedFetchSize());
  }

}
