/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.util.Optional;

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
      meanByteSize = meanByteSize / 2.0 + rowByteSize / 2.0;
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
