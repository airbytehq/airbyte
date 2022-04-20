package io.airbyte.integrations.source.relationaldb;

public class FetchSizeEstimator {

  private long fetchBufferBytes = 200 * 1024 * 1024 ; // 200 MB
  private int defaultFetchSize = 1000;
  private int minFetchSize = 10;
  private int maxFetchSize = 100_000;

  private FetchSizeEstimator() {
  }

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
