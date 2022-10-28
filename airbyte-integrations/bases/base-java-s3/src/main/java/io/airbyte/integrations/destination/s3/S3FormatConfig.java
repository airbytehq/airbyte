/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;

public interface S3FormatConfig {

  S3Format getFormat();

  String getFileExtension();

  static String withDefault(final JsonNode config, final String property, final String defaultValue) {
    final JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asText();
  }

  static int withDefault(final JsonNode config, final String property, final int defaultValue) {
    final JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asInt();
  }

  static boolean withDefault(final JsonNode config, final String property, final boolean defaultValue) {
    final JsonNode value = config.get(property);
    if (value == null || value.isNull()) {
      return defaultValue;
    }
    return value.asBoolean();
  }

}
