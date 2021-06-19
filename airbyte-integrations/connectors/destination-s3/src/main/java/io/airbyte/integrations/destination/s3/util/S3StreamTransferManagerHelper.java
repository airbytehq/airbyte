package io.airbyte.integrations.destination.s3.util;

import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;

public class S3StreamTransferManagerHelper {

  // See this doc about how they affect memory usage:
  // https://alexmojaki.github.io/s3-stream-upload/javadoc/apidocs/alex/mojaki/s3upload/StreamTransferManager.html
  // Total memory = (numUploadThreads + queueCapacity) * partSize + numStreams * (partSize + 6MB)
  // = 31 MB at current configurations
  public static final int DEFAULT_UPLOAD_THREADS = 2;
  public static final int DEFAULT_QUEUE_CAPACITY = 2;
  public static final int DEFAULT_PART_SIZE_MB = 5;
  public static final int DEFAULT_NUM_STREAMS = 1;

  public static StreamTransferManager getDefault(String bucketName, String objectKey, AmazonS3 s3Client) {
    // The stream transfer manager lets us greedily stream into S3. The native AWS SDK does not
    // have support for streaming multipart uploads. The alternative is first writing the entire
    // output to disk before loading into S3. This is not feasible with large input.
    // Data is chunked into parts during the upload. A part is sent off to a queue to be uploaded
    // once it has reached it's configured part size.
    return new StreamTransferManager(bucketName, objectKey, s3Client)
        .numStreams(DEFAULT_NUM_STREAMS)
        .queueCapacity(DEFAULT_QUEUE_CAPACITY)
        .numUploadThreads(DEFAULT_UPLOAD_THREADS)
        .partSize(DEFAULT_PART_SIZE_MB);
  }

}
