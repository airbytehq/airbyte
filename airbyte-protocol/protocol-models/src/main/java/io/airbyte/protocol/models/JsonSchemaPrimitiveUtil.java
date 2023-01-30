/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.BINARY_DATA_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.BOOLEAN_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.DATE_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.INTEGER_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.NUMBER_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.STRING_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TIMESTAMP_WITH_TIMEZONE_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TIME_WITHOUT_TIMEZONE_REFERENCE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TIME_WITH_TIMEZONE_REFERENCE;

import com.google.common.collect.BiMap;
import com.google.common.collect.ImmutableBiMap;
import com.google.common.collect.ImmutableSet;
import java.util.Set;

public class JsonSchemaPrimitiveUtil {

  public enum JsonSchemaPrimitive {
    // V0 schema primitives
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
      ImmutableSet.of(
          JsonSchemaPrimitive.STRING,
          JsonSchemaPrimitive.NUMBER,
          JsonSchemaPrimitive.OBJECT,
          JsonSchemaPrimitive.ARRAY,
          JsonSchemaPrimitive.BOOLEAN,
          JsonSchemaPrimitive.NULL);

  public static final boolean isV0Schema(final JsonSchemaPrimitive type) {
    return VO_JSON_SCHEMA_PRIMITIVE_SET.contains(type);
  }

  public static final BiMap<JsonSchemaPrimitive, String> PRIMITIVE_TO_REFERENCE_BIMAP =
      new ImmutableBiMap.Builder<JsonSchemaPrimitive, String>()
          .put(JsonSchemaPrimitive.STRING_V1, STRING_REFERENCE)
          .put(JsonSchemaPrimitive.BINARY_DATA_V1, BINARY_DATA_REFERENCE)
          .put(JsonSchemaPrimitive.DATE_V1, DATE_REFERENCE)
          .put(JsonSchemaPrimitive.TIMESTAMP_WITH_TIMEZONE_V1, TIMESTAMP_WITH_TIMEZONE_REFERENCE)
          .put(JsonSchemaPrimitive.TIMESTAMP_WITHOUT_TIMEZONE_V1, TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE)
          .put(JsonSchemaPrimitive.TIME_WITH_TIMEZONE_V1, TIME_WITH_TIMEZONE_REFERENCE)
          .put(JsonSchemaPrimitive.TIME_WITHOUT_TIMEZONE_V1, TIME_WITHOUT_TIMEZONE_REFERENCE)
          .put(JsonSchemaPrimitive.NUMBER_V1, NUMBER_REFERENCE)
          .put(JsonSchemaPrimitive.INTEGER_V1, INTEGER_REFERENCE)
          .put(JsonSchemaPrimitive.BOOLEAN_V1, BOOLEAN_REFERENCE)
          .build();

}
