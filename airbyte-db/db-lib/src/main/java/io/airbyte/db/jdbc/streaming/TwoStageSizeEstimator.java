/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import com.google.common.annotations.VisibleForTesting;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This estimator first uses the {@link InitialSizeEstimator} to calculate an initial fetch size by
 * sampling the first N rows consecutively, and then switches to {@link SamplingSizeEstimator} to
 * periodically adjust the fetch size by sampling every M rows.
 */
public class TwoStageSizeEstimator implements FetchSizeEstimator {

  private static final Logger LOGGER = LoggerFactory.getLogger(TwoStageSizeEstimator.class);

  private final int initialSampleSize;
  private BaseSizeEstimator delegate;
  private int counter = 0;

  public static TwoStageSizeEstimator getInstance() {
    return new TwoStageSizeEstimator();
  }

  private TwoStageSizeEstimator() {
    this.initialSampleSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE;
    this.delegate = new InitialSizeEstimator(
        FetchSizeConstants.MIN_BUFFER_BYTE_SIZE,
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
            getTargetBufferByteSize(Runtime.getRuntime().maxMemory()),
            FetchSizeConstants.SAMPLE_FREQUENCY,
            delegate.getMaxRowByteSize(),
            FetchSizeConstants.MIN_FETCH_SIZE,
            FetchSizeConstants.DEFAULT_FETCH_SIZE,
            FetchSizeConstants.MAX_FETCH_SIZE);
      }
    }

    delegate.accept(rowData);
  }

  @VisibleForTesting
  static long getTargetBufferByteSize(final Long maxMemory) {
    if (maxMemory == null || maxMemory == Long.MAX_VALUE) {
      LOGGER.info("No max memory limit found, use min JDBC buffer size: {}", FetchSizeConstants.MIN_BUFFER_BYTE_SIZE);
      return FetchSizeConstants.MIN_BUFFER_BYTE_SIZE;
    }
    final long targetBufferByteSize = Math.round(maxMemory * FetchSizeConstants.TARGET_BUFFER_SIZE_RATIO);
    final long finalBufferByteSize = Math.max(FetchSizeConstants.MIN_BUFFER_BYTE_SIZE, targetBufferByteSize);
    LOGGER.info("Max memory limit: {}, JDBC buffer size: {}", maxMemory, finalBufferByteSize);
    return finalBufferByteSize;
  }

  @VisibleForTesting
  BaseSizeEstimator getDelegate() {
    return delegate;
  }

}
