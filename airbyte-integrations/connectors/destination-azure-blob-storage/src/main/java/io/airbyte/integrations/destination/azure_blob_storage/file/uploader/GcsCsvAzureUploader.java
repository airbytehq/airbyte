/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.protocol.models.DestinationSyncMode;

public class GcsCsvAzureUploader extends AbstractGcsAzureUploader<GcsCsvWriter> {

  public GcsCsvAzureUploader(DestinationSyncMode syncMode,
                             GcsCsvWriter writer,
                             GcsDestinationConfig gcsDestinationConfig,
                             AppendBlobClient appendBlobClient,
                             boolean keepFilesInGcs,
                             int headerByteSize) {
    super(syncMode, writer, gcsDestinationConfig, appendBlobClient, keepFilesInGcs, headerByteSize);
  }

}
