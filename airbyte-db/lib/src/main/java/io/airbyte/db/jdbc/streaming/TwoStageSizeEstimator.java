/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import com.google.common.annotations.VisibleForTesting;
import java.util.Optional;

/**
 * This estimator first uses the {@link InitialSizeEstimator} to calculate an initial fetch size by
 * sampling the first N rows consecutively, and then switches to {@link SamplingSizeEstimator} to
 * periodically adjust the fetch size by sampling every M rows.
 */
public class TwoStageSizeEstimator implements FetchSizeEstimator {

  private final int initialSampleSize;
  private BaseSizeEstimator delegate;
  private int counter = 0;

  public static TwoStageSizeEstimator getInstance() {
    return new TwoStageSizeEstimator();
  }

  private TwoStageSizeEstimator() {
    this.initialSampleSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE;
    this.delegate = new InitialSizeEstimator(
        FetchSizeConstants.TARGET_BUFFER_BYTE_SIZE,
        initialSampleSize,
        FetchSizeConstants.MIN_FETCH_SIZE,
        FetchSizeConstants.DEFAULT_FETCH_SIZE,
        FetchSizeConstants.MAX_FETCH_SIZE);
  }

  @Override
  public Optional<Integer> getFetchSize() {
    return delegate.getFetchSize();
  }

  @Override
  public void accept(final Object rowData) {
    if (counter <= initialSampleSize + 1) {
      counter++;
      // switch to SamplingSizeEstimator after the initial N rows
      if (delegate instanceof InitialSizeEstimator && counter > initialSampleSize) {
        delegate = new SamplingSizeEstimator(
            FetchSizeConstants.TARGET_BUFFER_BYTE_SIZE,
            FetchSizeConstants.POST_INITIAL_SAMPLE_SIZE,
            FetchSizeConstants.SAMPLE_FREQUENCY,
            delegate.getMeanRowByteSize(),
            FetchSizeConstants.MIN_FETCH_SIZE,
            FetchSizeConstants.DEFAULT_FETCH_SIZE,
            FetchSizeConstants.MAX_FETCH_SIZE);
      }
    }

    delegate.accept(rowData);
  }

  @VisibleForTesting
  BaseSizeEstimator getDelegate() {
    return delegate;
  }

}
