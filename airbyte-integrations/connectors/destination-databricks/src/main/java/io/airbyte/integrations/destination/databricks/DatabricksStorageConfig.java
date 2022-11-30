/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksStorageConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStorageConfig.class);

  public static DatabricksStorageConfig getDatabricksStorageConfig(final JsonNode config) {
    final JsonNode typeConfig = config.get("data_source_type");
    LOGGER.info("Databricks storage type config: {}", typeConfig.toString());
    final DatabricksStorageType storageType = DatabricksStorageType
        .valueOf(typeConfig.asText().toUpperCase());

    switch (storageType) {
      case S3 -> {
        return new DatabricksS3StorageConfig(config);
      }
      case AZURE_BLOB_STORAGE -> {
        return new DatabricksAzureBlobStorageConfig(config);
      }
      default -> {
        throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
      }
    }
  }

  public AzureBlobStorageConfig getAzureBlobStorageConfigOrThrow() {
    throw new UnsupportedOperationException("Cannot get Azure Blob Storage config from " + this.getClass().getSimpleName());
  }

  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    throw new UnsupportedOperationException("Cannot get S3 destination config from " + this.getClass().getSimpleName());
  }

}
