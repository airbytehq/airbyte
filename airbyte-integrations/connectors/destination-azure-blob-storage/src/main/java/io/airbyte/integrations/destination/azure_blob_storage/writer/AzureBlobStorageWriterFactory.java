/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;

/**
 * Create different {@link AzureBlobStorageWriter} based on
 * {@link AzureBlobStorageDestinationConfig}.
 */
public interface AzureBlobStorageWriterFactory {

  AzureBlobStorageWriter create(AzureBlobStorageDestinationConfig config,
                                AppendBlobClient appendBlobClient,
                                ConfiguredAirbyteStream configuredStream,
                                boolean isNewlyCreatedBlob)
      throws Exception;

}
