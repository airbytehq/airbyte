/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormat;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormatConfig;

public class AzureBlobStorageCsvFormatConfig implements AzureBlobStorageFormatConfig {

  public enum Flattening {

    // These values must match the format / csv_flattening enum values in spec.json.
    NO("No flattening"),
    ROOT_LEVEL("Root level flattening");

    private final String value;

    Flattening(final String value) {
      this.value = value;
    }

    @JsonCreator
    public static Flattening fromValue(final String value) {
      for (final Flattening f : Flattening.values()) {
        if (f.value.equalsIgnoreCase(value)) {
          return f;
        }
      }
      throw new IllegalArgumentException("Unexpected value: " + value);
    }

    public String getValue() {
      return value;
    }

  }

  private final Flattening flattening;
  private final boolean fileExtensionRequired;

  public AzureBlobStorageCsvFormatConfig(final JsonNode formatConfig) {
    this.flattening = Flattening.fromValue(formatConfig.get("flattening").asText());
    this.fileExtensionRequired = formatConfig.has("file_extension") ? formatConfig.get("file_extension").asBoolean() : false;
  }

  public boolean isFileExtensionRequired() {
    return fileExtensionRequired;
  }

  @Override
  public AzureBlobStorageFormat getFormat() {
    return AzureBlobStorageFormat.CSV;
  }

  public Flattening getFlattening() {
    return flattening;
  }

  @Override
  public String toString() {
    return "AzureBlobStorageCsvFormatConfig{" +
        "flattening=" + flattening +
        ", fileExtensionRequired=" + fileExtensionRequired +
        '}';
  }

}
