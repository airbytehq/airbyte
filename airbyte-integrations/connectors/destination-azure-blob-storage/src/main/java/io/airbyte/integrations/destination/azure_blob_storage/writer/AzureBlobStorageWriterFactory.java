/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

/**
 * Create different {@link AzureBlobStorageWriter} based on
 * {@link AzureBlobStorageDestinationConfig}.
 */
public interface AzureBlobStorageWriterFactory {

  AzureBlobStorageWriter create(AzureBlobStorageDestinationConfig config,
                                AppendBlobClient appendBlobClient,
                                ConfiguredAirbyteStream configuredStream)
      throws Exception;

}
