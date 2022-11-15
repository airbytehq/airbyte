/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.google.common.collect.BiMap;
import com.google.common.collect.ImmutableBiMap;
import com.google.common.collect.ImmutableSet;
import java.util.Set;

public class JsonSchemaPrimitiveUtil {

  public enum JsonSchemaPrimitive {

    STRING,
    NUMBER,
    OBJECT,
    ARRAY,
    BOOLEAN,
    NULL,
    // V1 schema primitives
    STRING_V1,
    BINARY_DATA_V1,
    DATE_V1,
    TIMESTAMP_WITH_TIMEZONE_V1,
    TIMESTAMP_WITHOUT_TIMEZONE_V1,
    TIME_WITH_TIMEZONE_V1,
    TIME_WITHOUT_TIMEZONE_V1,
    NUMBER_V1,
    INTEGER_V1,
    BOOLEAN_V1;
  }

  public static final Set<JsonSchemaPrimitive> VO_JSON_SCHEMA_PRIMITIVE_SET =
      ImmutableSet.of(JsonSchemaPrimitive.STRING, JsonSchemaPrimitive.NUMBER,
          JsonSchemaPrimitive.OBJECT, JsonSchemaPrimitive.ARRAY, JsonSchemaPrimitive.BOOLEAN, JsonSchemaPrimitive.NULL);

  public static final boolean isV0Schema(final JsonSchemaPrimitive type) {
    return VO_JSON_SCHEMA_PRIMITIVE_SET.contains(type);
  }

  public static final BiMap<JsonSchemaPrimitive, String> PRIMITIVE_TO_REFERENCE_BIMAP =
      new ImmutableBiMap.Builder<JsonSchemaPrimitive, String>()
          .put(JsonSchemaPrimitive.STRING_V1, "WellKnownTypes.json#definitions/String")
          .put(JsonSchemaPrimitive.BINARY_DATA_V1, "WellKnownTypes.json#definitions/BinaryData")
          .put(JsonSchemaPrimitive.DATE_V1, "WellKnownTypes.json#definitions/Date")
          .put(JsonSchemaPrimitive.TIMESTAMP_WITH_TIMEZONE_V1, "WellKnownTypes.json#definitions/TimestampWithTimezone")
          .put(JsonSchemaPrimitive.TIMESTAMP_WITHOUT_TIMEZONE_V1, "WellKnownTypes.json#definitions/TimestampWithoutTimezone")
          .put(JsonSchemaPrimitive.TIME_WITH_TIMEZONE_V1, "WellKnownTypes.json#definitions/TimeWithTimezone")
          .put(JsonSchemaPrimitive.TIME_WITHOUT_TIMEZONE_V1, "WellKnownTypes.json#definitions/TimeWithoutTimezone")
          .put(JsonSchemaPrimitive.NUMBER_V1, "WellKnownTypes.json#definitions/Number")
          .put(JsonSchemaPrimitive.INTEGER_V1, "WellKnownTypes.json#definitions/Integer")
          .put(JsonSchemaPrimitive.BOOLEAN_V1, "WellKnownTypes.json#definitions/Boolean")
          .build();

}
