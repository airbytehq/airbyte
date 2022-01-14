/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractGcsAzureUploader<T extends S3Writer> extends AbstractAzureUploader<S3Writer> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractGcsAzureUploader.class);

  protected final GcsDestinationConfig gcsDestinationConfig;

  AbstractGcsAzureUploader(T writer,
                           GcsDestinationConfig gcsDestinationConfig,
                           AppendBlobClient appendBlobClient,
                           boolean keepFilesInGcs,
                           int headerByteSize) {
    super(writer, keepFilesInGcs, appendBlobClient, headerByteSize);
    this.gcsDestinationConfig = gcsDestinationConfig;
  }

  @Override
  protected AmazonS3 getS3Client() {
    final GcsDestinationConfig gcsDestinationConfig = this.gcsDestinationConfig;
    return GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
  }

  @Override
  protected String getBucketName() {
    return gcsDestinationConfig.getBucketName();
  }

  @Override
  protected String getBucketPath() {
    return gcsDestinationConfig.getBucketPath();
  }

}
