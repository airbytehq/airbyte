/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;

public interface AzureBlobStorageFormatConfig {

  AzureBlobStorageFormat getFormat();

  static String withDefault(JsonNode config, String property, String defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asText();
  }

  static int withDefault(JsonNode config, String property, int defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asInt();
  }

  static boolean withDefault(JsonNode config, String property, boolean defaultValue) {
    JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asBoolean();
  }

}
