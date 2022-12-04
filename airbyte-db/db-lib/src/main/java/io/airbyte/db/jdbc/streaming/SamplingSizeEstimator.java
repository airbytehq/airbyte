/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.util.Optional;

/**
 * This class adjusts the max row byte size by measuring one row out of every
 * {@code sampleFrequency} rows.
 */
public class SamplingSizeEstimator extends BaseSizeEstimator implements FetchSizeEstimator {

  private final int sampleFrequency;

  private int counter = 0;
  private boolean hasNewEstimation = false;

  public SamplingSizeEstimator(final long bufferByteSize,
                               final int sampleFrequency,
                               final double initialRowByteSize,
                               final int minFetchSize,
                               final int defaultFetchSize,
                               final int maxFetchSize) {
    super(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize);
    this.sampleFrequency = sampleFrequency;
    this.maxRowByteSize = initialRowByteSize;
  }

  @Override
  public void accept(final Object row) {
    counter++;
    if (counter < sampleFrequency) {
      return;
    }

    counter = 0;
    final long rowByteSize = getEstimatedByteSize(row);
    if (this.maxRowByteSize < rowByteSize) {
      this.maxRowByteSize = rowByteSize;
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
