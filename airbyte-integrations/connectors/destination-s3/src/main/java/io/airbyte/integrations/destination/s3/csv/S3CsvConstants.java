package io.airbyte.integrations.destination.s3.csv;

public class S3CsvConstants {

  // These parameters are used by {@link StreamTransferManager}.
  // See this doc about how they affect memory usage:
  // https://alexmojaki.github.io/s3-stream-upload/javadoc/apidocs/alex/mojaki/s3upload/StreamTransferManager.html
  // Total memory = (numUploadThreads + queueCapacity) * partSize + numStreams * (partSize + 6MB)
  // = 31 MB at current configurations
  public static final int DEFAULT_UPLOAD_THREADS = 2;
  public static final int DEFAULT_QUEUE_CAPACITY = 2;
  public static final int DEFAULT_PART_SIZE_MB = 5;
  public static final int DEFAULT_NUM_STREAMS = 1;

}
