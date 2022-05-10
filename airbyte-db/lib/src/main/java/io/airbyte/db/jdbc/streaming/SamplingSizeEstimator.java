/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.util.Optional;

/**
 * This class adjusts the mean row byte size by estimating one row out of every
 * {@code sampleFrequency} rows.
 */
public class SamplingSizeEstimator extends BaseSizeEstimator implements FetchSizeEstimator {

  private final int sampleSize;
  private final int sampleFrequency;

  private int counter = 0;
  private boolean hasNewEstimation = false;

  public SamplingSizeEstimator(final long bufferByteSize,
                               final int sampleSize,
                               final int sampleFrequency,
                               final double initialRowByteSize,
                               final int minFetchSize,
                               final int defaultFetchSize,
                               final int maxFetchSize) {
    super(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize);
    this.sampleSize = sampleSize;
    this.sampleFrequency = sampleFrequency;
    this.meanByteSize = initialRowByteSize;
  }

  @Override
  public void accept(final Object row) {
    counter++;
    if (counter < sampleFrequency) {
      return;
    }

    counter = 0;
    final long rowByteSize = getEstimatedByteSize(row);
    if (rowByteSize != Math.round(meanByteSize)) {
      // This is equivalent to calculating the mean size
      // based on the last N rows. The division is performed
      // first to prevent overflow.
      meanByteSize = meanByteSize / sampleSize * (sampleSize - 1) + 1.0 * rowByteSize / sampleSize;
      hasNewEstimation = true;
    }
  }

  @Override
  public Optional<Integer> getFetchSize() {
    if (!hasNewEstimation) {
      return Optional.empty();
    }

    hasNewEstimation = false;
    return Optional.of(getBoundedFetchSize());
  }

}
