/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Optional;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;

public class IncrementalUtils {

  private static final String PROPERTIES = "properties";

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public static String getCursorField(final ConfiguredAirbyteStream stream) {
    if (stream.getCursorField().size() == 0) {
      throw new IllegalStateException("No cursor field specified for stream attempting to do incremental.");
    } else if (stream.getCursorField().size() > 1) {
      throw new IllegalStateException("Source does not support nested cursor fields.");
    } else {
      return stream.getCursorField().get(0);
    }
  }

  public static Optional<String> getCursorFieldOptional(final ConfiguredAirbyteStream stream) {
    try {
      return Optional.ofNullable(getCursorField(stream));
    } catch (final IllegalStateException e) {
      return Optional.empty();
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

    if (stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("type") == null &&
        stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("$ref") == null) {
      throw new IllegalStateException(
          String.format("Could not find cursor type for field: %s in schema for stream: %s.", cursorField, stream.getStream().getName()));
    }

    if (stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("type") == null) {
      return JsonSchemaPrimitiveUtil.PRIMITIVE_TO_REFERENCE_BIMAP.inverse()
          .get(stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("$ref").asText());
    } else {
      return JsonSchemaPrimitive.valueOf(stream.getStream().getJsonSchema().get(PROPERTIES).get(cursorField).get("type").asText().toUpperCase());
    }
  }

  /**
   * Comparator where if original is less than candidate then value less than 0, if greater than
   * candidate then value greater than 0, else 0
   *
   * @param original the first value to compare
   * @param candidate the second value to compare
   * @param type primitive type used to determine comparison
   * @return
   */
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

    if (original.startsWith("ctid:")) {
      final var originalCtid = toTuple(original);
      final var candidateCtid = toTuple(candidate);
      return originalCtid.compareTo(candidateCtid);
    }
    switch (type) {
      case STRING, STRING_V1, DATE_V1, TIME_WITH_TIMEZONE_V1, TIME_WITHOUT_TIMEZONE_V1, TIMESTAMP_WITH_TIMEZONE_V1, TIMESTAMP_WITHOUT_TIMEZONE_V1 -> {
        return original.compareTo(candidate);
      }
      case NUMBER, NUMBER_V1, INTEGER_V1 -> {
        // todo (cgardens) - handle big decimal. this is currently an overflow risk.
        return Double.compare(Double.parseDouble(original), Double.parseDouble(candidate));
      }
      case BOOLEAN, BOOLEAN_V1 -> {
        return Boolean.compare(Boolean.parseBoolean(original), Boolean.parseBoolean(candidate));
      }
      // includes OBJECT, ARRAY, NULL
      default -> throw new IllegalStateException(String.format("Cannot use field of type %s as a comparable", type));
    }
  }

  private static Pair<Long, Long> toTuple(final String ctid) {
    final var trimmed = StringUtils.replace(StringUtils.replace(ctid, "ctid:(", ""), ")", "");
    final var comp = trimmed.split(",");
    return Pair.of(Long.valueOf(comp[0]), Long.valueOf(comp[1]));

  }

}
