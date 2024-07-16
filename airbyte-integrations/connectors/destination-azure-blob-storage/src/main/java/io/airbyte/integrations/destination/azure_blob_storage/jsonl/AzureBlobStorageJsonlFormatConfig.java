/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.jsonl;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormat;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormatConfig;

public class AzureBlobStorageJsonlFormatConfig implements AzureBlobStorageFormatConfig {

  private final boolean fileExtensionRequired;

  public AzureBlobStorageJsonlFormatConfig(final JsonNode formatConfig) {
    this.fileExtensionRequired = formatConfig.has("file_extension") ? formatConfig.get("file_extension").asBoolean() : false;
  }

  @Override
  public boolean isFileExtensionRequired() {
    return fileExtensionRequired;
  }

  @Override
  public AzureBlobStorageFormat getFormat() {
    return AzureBlobStorageFormat.JSONL;
  }

  @Override
  public String toString() {
    return "AzureBlobStorageJsonlFormatConfig{" +
        "fileExtensionRequired=" + fileExtensionRequired +
        '}';
  }

}
