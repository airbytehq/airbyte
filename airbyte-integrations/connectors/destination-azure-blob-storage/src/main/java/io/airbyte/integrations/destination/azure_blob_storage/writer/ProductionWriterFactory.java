/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormat;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvWriter;
import io.airbyte.integrations.destination.azure_blob_storage.jsonl.AzureBlobStorageJsonlWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements AzureBlobStorageWriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public AzureBlobStorageWriter create(AzureBlobStorageDestinationConfig config,
                                       AppendBlobClient appendBlobClient,
                                       ConfiguredAirbyteStream configuredStream,
                                       boolean isNewlyCreatedBlob)
      throws Exception {
    AzureBlobStorageFormat format = config.getFormatConfig().getFormat();

    if (format == AzureBlobStorageFormat.CSV) {
      LOGGER.debug("Picked up CSV format writer");
      return new AzureBlobStorageCsvWriter(config, appendBlobClient, configuredStream,
          isNewlyCreatedBlob);
    }

    if (format == AzureBlobStorageFormat.JSONL) {
      LOGGER.debug("Picked up JSONL format writer");
      return new AzureBlobStorageJsonlWriter(config, appendBlobClient, configuredStream,
          isNewlyCreatedBlob);
    }

    throw new RuntimeException("Unexpected AzureBlobStorage destination format: " + format);
  }

}
