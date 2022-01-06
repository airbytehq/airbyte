/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.file.formatter.AzureRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.jsonl.GcsJsonlWriter;
import io.airbyte.protocol.models.DestinationSyncMode;

public class GcsJsonlAzureUploader extends AbstractGcsAzureUploader<GcsJsonlWriter> {

  public GcsJsonlAzureUploader(DestinationSyncMode syncMode,
                               GcsJsonlWriter writer,
                               GcsDestinationConfig gcsDestinationConfig,
                               AppendBlobClient appendBlobClient,
                               boolean keepFilesInGcs,
                               AzureRecordFormatter recordFormatter) {
    super(syncMode, writer, gcsDestinationConfig, appendBlobClient, keepFilesInGcs, recordFormatter);
  }
}
