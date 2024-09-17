/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig;
import io.airbyte.integrations.destination.azure_blob_storage.jsonl.AzureBlobStorageJsonlFormatConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageFormatConfigs {

  private AzureBlobStorageFormatConfigs() {

  }

  protected static final Logger LOGGER = LoggerFactory
      .getLogger(AzureBlobStorageFormatConfigs.class);

  public static AzureBlobStorageFormatConfig getAzureBlobStorageFormatConfig(final JsonNode config) {
    final JsonNode formatConfig = config.get("format");
    LOGGER.info("Azure Blob Storage format config: {}", formatConfig.toString());
    final AzureBlobStorageFormat formatType = AzureBlobStorageFormat
        .valueOf(formatConfig.get("format_type").asText().toUpperCase());

    switch (formatType) {
      case CSV -> {
        return new AzureBlobStorageCsvFormatConfig(formatConfig);
      }
      case JSONL -> {
        return new AzureBlobStorageJsonlFormatConfig(formatConfig);
      }
      default -> throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));

    }
  }

}
