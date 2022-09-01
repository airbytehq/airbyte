/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.JsonSchemaPrimitive;

public class IncrementalUtils {

  private static final String PROPERTIES = "properties";

  public static String getCursorField(final ConfiguredAirbyteStream stream) {
    if (stream.getCursorField().size() == 0) {
      throw new IllegalStateException("No cursor field specified for stream attempting to do incremental.");
    } else if (stream.getCursorField().size() > 1) {
      throw new IllegalStateException("Source does not support nested cursor fields.");
    } else {
      return stream.getCursorField().get(0);
    }
  }

  public static JsonSchemaPrimitive getCursorType(final ConfiguredAirbyteStream stream, final String cursorField) {
    if (stream.getStream().getJsonSchema().get(PROPERTIES) == null) {
      throw new IllegalStateException(String.format("No properties found in stream: %s.", stream.getStream().getName()));
    }

    if (stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField) == null) {
      throw new IllegalStateException(
          String.format("Could not find cursor field: %s in schema for stream: %s.", cursorField, stream.getStream().getName()));
    }

    if (stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("type") == null) {
      throw new IllegalStateException(
          String.format("Could not find cursor type for field: %s in schema for stream: %s.", cursorField, stream.getStream().getName()));
    }

    return JsonSchemaPrimitive.valueOf(stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("type").asText().toUpperCase());
  }

  // x < 0 mean replace original
  // x == 0 means keep original
  // x > 0 means keep original
  public static int compareCursors(final String original, final String candidate, final JsonSchemaPrimitive type) {
    if (original == null && candidate == null) {
      return 0;
    }

    if (candidate == null) {
      return 1;
    }

    if (original == null) {
      return -1;
    }

    switch (type) {
      case STRING -> {
        return original.compareTo(candidate);
      }
      case NUMBER -> {
        // todo (cgardens) - handle big decimal. this is currently an overflow risk.
        return Double.compare(Double.parseDouble(original), Double.parseDouble(candidate));
      }
      case BOOLEAN -> {
        return Boolean.compare(Boolean.parseBoolean(original), Boolean.parseBoolean(candidate));
      }
      // includes OBJECT, ARRAY, NULL
      default -> throw new IllegalStateException(String.format("Cannot use field of type %s as a comparable", type));
    }
  }

}
