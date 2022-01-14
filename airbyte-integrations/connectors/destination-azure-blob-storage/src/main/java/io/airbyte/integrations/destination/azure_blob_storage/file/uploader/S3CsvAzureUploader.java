/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;

public class S3CsvAzureUploader extends AbstractS3AzureUploader<S3CsvWriter> {

  public S3CsvAzureUploader(S3CsvWriter writer,
                            S3DestinationConfig s3DestinationConfig,
                            AppendBlobClient appendBlobClient,
                            boolean keepFilesInS3,
                            int headerByteSize) {
    super(writer, s3DestinationConfig, appendBlobClient, keepFilesInS3, headerByteSize);
  }

}
