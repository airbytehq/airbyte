package io.airbyte.integrations.destination.s3;

import java.text.DateFormat;
import java.text.SimpleDateFormat;

public final class S3DestinationConstants {

  public static final int DEFAULT_PART_SIZE_MB = 10;
  public static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  public static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;
  public static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");

  private S3DestinationConstants() {}

}
