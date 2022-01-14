/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractS3AzureUploader<T extends S3Writer> extends AbstractAzureUploader<S3Writer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractS3AzureUploader.class);

  protected final S3DestinationConfig s3DestinationConfig;

  AbstractS3AzureUploader(T writer,
                          S3DestinationConfig s3DestinationConfig,
                          AppendBlobClient appendBlobClient,
                          boolean keepFilesInS3,
                          int headerByteSize) {
    super(writer, keepFilesInS3, appendBlobClient, headerByteSize);
    this.s3DestinationConfig = s3DestinationConfig;
  }

  @Override
  protected AmazonS3 getS3Client() {
    return s3DestinationConfig.getS3Client();
  }

  @Override
  protected String getBucketName() {
    return s3DestinationConfig.getBucketName();
  }

  @Override
  protected String getBucketPath() {
    return s3DestinationConfig.getBucketPath();
  }

}
