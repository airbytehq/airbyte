/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3StreamTransferManagerHelper {

  protected static final Logger LOGGER = LoggerFactory.getLogger(S3StreamTransferManagerHelper.class);

  // See this doc about how they affect memory usage:
  // https://alexmojaki.github.io/s3-stream-upload/javadoc/apidocs/alex/mojaki/s3upload/StreamTransferManager.html
  // Total memory = (numUploadThreads + queueCapacity) * partSize + numStreams * (partSize + 6MB)
  // = 31 MB at current configurations
  public static final int DEFAULT_UPLOAD_THREADS = 2;
  public static final int DEFAULT_QUEUE_CAPACITY = 2;
  public static final int DEFAULT_PART_SIZE_MB = 5;
  // MAX object size for AWS and GCS is 5TB (max allowed 10,000 parts*525mb)
  // (https://aws.amazon.com/s3/faqs/, https://cloud.google.com/storage/quotas)
  public static final int MAX_ALLOWED_PART_SIZE_MB = 525;
  public static final int DEFAULT_NUM_STREAMS = 1;

  public static StreamTransferManager getDefault(String bucketName, String objectKey, AmazonS3 s3Client, Long partSize) {
    if (partSize == null) {
      LOGGER.warn(String.format("Part size for StreamTransferManager is not set explicitly. Will use the default one = %sMB. "
          + "Please note server allows up to 10,000 parts to be uploaded for a single object, i.e. 50GB for stream. "
          + "Feel free to increase partSize arg, but make sure you have enough memory resources allocated", DEFAULT_PART_SIZE_MB));
      return getDefault(bucketName, objectKey, s3Client);
    }
    if (partSize < DEFAULT_PART_SIZE_MB) {
      LOGGER.warn(String.format("By the server limitation part size can't be less than %sMB which is already set by default. "
          + "Will use the default value", DEFAULT_PART_SIZE_MB));
      return getDefault(bucketName, objectKey, s3Client);
    }
    if (partSize > MAX_ALLOWED_PART_SIZE_MB) {
      LOGGER.warn(
          "Server allows up to 10,000 parts to be uploaded for a single object, and each part must be identified by a unique number from 1 to 10,000."
              + " These part numbers are allocated evenly by the manager to each output stream. Therefore the maximum amount of"
              + " data that can be written to a stream is 10000/numStreams * partSize. If you try to write more, an IndexOutOfBoundsException"
              + " will be thrown. The total object size can be at most 5 TB, so there is no reason to set this higher"
              + " than 525MB. If you're using more streams, you may want a higher value in case some streams get more data than others. "
              + "So will use max allowed value =" + MAX_ALLOWED_PART_SIZE_MB);
      return new StreamTransferManager(bucketName, objectKey, s3Client)
          .numStreams(DEFAULT_NUM_STREAMS)
          .queueCapacity(DEFAULT_QUEUE_CAPACITY)
          .numUploadThreads(DEFAULT_UPLOAD_THREADS)
          .partSize(MAX_ALLOWED_PART_SIZE_MB);
    }

    LOGGER.info(String.format("PartSize arg is set to %s MB", partSize));
    return new StreamTransferManager(bucketName, objectKey, s3Client)
        .numStreams(DEFAULT_NUM_STREAMS)
        .queueCapacity(DEFAULT_QUEUE_CAPACITY)
        .numUploadThreads(DEFAULT_UPLOAD_THREADS)
        .partSize(partSize);
  }

  private static StreamTransferManager getDefault(String bucketName, String objectKey, AmazonS3 s3Client) {
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
