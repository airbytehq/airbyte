/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.databricks.azure.DatabricksAzureBlobStorageConfigProvider;
import io.airbyte.integrations.destination.databricks.s3.DatabricksS3StorageConfigProvider;
import io.airbyte.integrations.destination.databricks.utils.DatabricksConstants;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksStorageConfigProvider {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStorageConfigProvider.class);

  public static DatabricksStorageConfigProvider getDatabricksStorageConfig(final JsonNode config) {
    final JsonNode typeConfig = config.get(DatabricksConstants.DATABRICKS_DATA_SOURCE_TYPE_KEY);
    LOGGER.info("Databricks storage type config: {}", typeConfig.toString());
    return switch (DatabricksStorageType.valueOf(typeConfig.asText())) {
      case MANAGED_TABLES_STORAGE -> null; // No need for extra storage config
      case S3_STORAGE -> new DatabricksS3StorageConfigProvider(config);
      case AZURE_BLOB_STORAGE -> new DatabricksAzureBlobStorageConfigProvider(config);
    };
  }

  public AzureBlobStorageConfig getAzureBlobStorageConfigOrThrow() {
    throw new UnsupportedOperationException("Cannot get Azure Blob Storage config from " + this.getClass().getSimpleName());
  }

  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    throw new UnsupportedOperationException("Cannot get S3 destination config from " + this.getClass().getSimpleName());
  }

}
