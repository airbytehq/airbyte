/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import java.util.Collections;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StreamTransferManagerFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(StreamTransferManagerFactory.class);

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

  public static Builder create(final String bucketName,
                               final String objectKey,
                               final AmazonS3 s3Client) {
    return new Builder(bucketName, objectKey, s3Client);
  }

  public static class Builder {

    private final String bucketName;
    private final String objectKey;
    private final AmazonS3 s3Client;
    private Map<String, String> userMetadata;
    private long partSize = DEFAULT_PART_SIZE_MB;

    private Builder(final String bucketName,
                    final String objectKey,
                    final AmazonS3 s3Client) {
      this.bucketName = bucketName;
      this.objectKey = objectKey;
      this.s3Client = s3Client;
    }

    public Builder setPartSize(final Long partSize) {
      if (partSize == null) {
        this.partSize = DEFAULT_PART_SIZE_MB;
      } else if (partSize < DEFAULT_PART_SIZE_MB) {
        LOGGER.warn("Part size {} is smaller than the minimum allowed, default to {}", partSize, DEFAULT_PART_SIZE_MB);
        this.partSize = DEFAULT_PART_SIZE_MB;
      } else if (partSize > MAX_ALLOWED_PART_SIZE_MB) {
        LOGGER.warn("Part size {} is larger than the maximum allowed, default to {}", partSize, MAX_ALLOWED_PART_SIZE_MB);
        this.partSize = MAX_ALLOWED_PART_SIZE_MB;
      } else {
        this.partSize = partSize;
      }
      return this;
    }

    public Builder setUserMetadata(final Map<String, String> userMetadata) {
      this.userMetadata = userMetadata;
      return this;
    }

    public StreamTransferManager get() {
      if (userMetadata == null) {
        userMetadata = Collections.emptyMap();
      }
      return new StreamTransferManagerWithMetadata(bucketName, objectKey, s3Client, userMetadata)
          .numStreams(DEFAULT_NUM_STREAMS)
          .queueCapacity(DEFAULT_QUEUE_CAPACITY)
          .numUploadThreads(DEFAULT_UPLOAD_THREADS)
          .partSize(partSize);
    }

  }

}
