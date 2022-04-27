package io.airbyte.db.jdbc.streaming;

public final class FetchSizeConstants {

  public static final long BUFFER_BYTE_SIZE = 200L * 1024L * 1024L; // 200 MB
  public static final int INITIAL_SAMPLE_SIZE = 10;
  public static final int SAMPLE_FREQUENCY = 100;
  public static final int MIN_FETCH_SIZE = 10;
  public static final int DEFAULT_FETCH_SIZE = 1000;
  public static final int MAX_FETCH_SIZE = 100_000;

  private FetchSizeConstants() {
  }

}
