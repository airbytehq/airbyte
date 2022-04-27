package io.airbyte.db.jdbc.streaming;

import com.google.common.annotations.VisibleForTesting;
import java.util.Optional;

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
        FetchSizeConstants.BUFFER_BYTE_SIZE,
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
      if (delegate instanceof InitialSizeEstimator && counter > initialSampleSize) {
        delegate = new SamplingSizeEstimator(
            FetchSizeConstants.BUFFER_BYTE_SIZE,
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
