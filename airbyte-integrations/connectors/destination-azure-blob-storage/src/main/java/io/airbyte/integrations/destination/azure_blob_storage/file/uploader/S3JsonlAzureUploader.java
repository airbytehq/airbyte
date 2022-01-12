/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlWriter;
import io.airbyte.protocol.models.DestinationSyncMode;

public class S3JsonlAzureUploader extends AbstractS3AzureUploader<S3JsonlWriter> {

  public S3JsonlAzureUploader(DestinationSyncMode syncMode,
                              S3JsonlWriter writer,
                              S3DestinationConfig s3DestinationConfig,
                              AppendBlobClient appendBlobClient,
                              boolean keepFilesInS3,
                              int headerByteSize) {
    super(syncMode, writer, s3DestinationConfig, appendBlobClient, keepFilesInS3, headerByteSize);
  }

}
