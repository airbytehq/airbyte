/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import java.util.Arrays;
import java.util.List;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import org.apache.avro.Schema;

/**
 * Mapping of JsonSchema types to Avro types.
 */
public enum JsonSchemaType {

  STRING_V1("WellKnownTypes.json#/definitions/String", Schema.Type.STRING),
  INTEGER_V1("WellKnownTypes.json#/definitions/Integer", Schema.Type.INT),
  NUMBER_V1("WellKnownTypes.json#/definitions/Number", Schema.Type.DOUBLE),
  BOOLEAN_V1("WellKnownTypes.json#/definitions/Boolean", Schema.Type.BOOLEAN),
  BINARY_DATA_V1("WellKnownTypes.json#/definitions/BinaryData", Schema.Type.BYTES),
  DATE_V1("WellKnownTypes.json#/definitions/Date", Schema.Type.INT),
  TIMESTAMP_WITH_TIMEZONE_V1("WellKnownTypes.json#/definitions/TimestampWithTimezone", Schema.Type.LONG),
  TIMESTAMP_WITHOUT_TIMEZONE_V1("WellKnownTypes.json#/definitions/TimestampWithoutTimezone", Schema.Type.LONG),
  TIME_WITH_TIMEZONE_V1("WellKnownTypes.json#/definitions/TimeWithTimezone", Schema.Type.STRING),
  TIME_WITHOUT_TIMEZONE_V1("WellKnownTypes.json#/definitions/TimeWithoutTimezone", Schema.Type.LONG),
  OBJECT("object", Schema.Type.RECORD),
  ARRAY("array", Schema.Type.ARRAY),
  COMBINED("combined", Schema.Type.UNION),
  @Deprecated
  STRING_V0("string", null, Schema.Type.STRING),
  @Deprecated
  NUMBER_INT_V0("number", "integer", Schema.Type.INT),
  @Deprecated
  NUMBER_BIGINT_V0("string", "big_integer", Schema.Type.STRING),
  @Deprecated
  NUMBER_FLOAT_V0("number", "float", Schema.Type.FLOAT),
  @Deprecated
  NUMBER_V0("number", null, Schema.Type.DOUBLE),
  @Deprecated
  INTEGER_V0("integer", null, Schema.Type.INT),
  @Deprecated
  BOOLEAN_V0("boolean", null, Schema.Type.BOOLEAN),
  @Deprecated
  NULL("null", null, Schema.Type.NULL);

  private final String jsonSchemaType;
  private final Schema.Type avroType;
  private String jsonSchemaAirbyteType;

  JsonSchemaType(final String jsonSchemaType, final String jsonSchemaAirbyteType, final Schema.Type avroType) {
    this.jsonSchemaType = jsonSchemaType;
    this.jsonSchemaAirbyteType = jsonSchemaAirbyteType;
    this.avroType = avroType;
  }

  JsonSchemaType(final String jsonSchemaType, final Schema.Type avroType) {
    this.jsonSchemaType = jsonSchemaType;
    this.avroType = avroType;
  }

  public static JsonSchemaType fromJsonSchemaType(final String jsonSchemaType) {
    return fromJsonSchemaType(jsonSchemaType, null);
  }

  public static JsonSchemaType fromJsonSchemaType(final @Nonnull String jsonSchemaType, final @Nullable String jsonSchemaAirbyteType) {
    List<JsonSchemaType> matchSchemaType = null;
    // Match by Type + airbyteType
    if (jsonSchemaAirbyteType != null) {
      matchSchemaType = Arrays.stream(values())
          .filter(type -> jsonSchemaType.equals(type.jsonSchemaType))
          .filter(type -> jsonSchemaAirbyteType.equals(type.jsonSchemaAirbyteType))
          .toList();
    }

    // Match by Type are no results already
    if (matchSchemaType == null || matchSchemaType.isEmpty()) {
      matchSchemaType =
          Arrays.stream(values()).filter(format -> jsonSchemaType.equals(format.jsonSchemaType) && format.jsonSchemaAirbyteType == null).toList();
    }

    if (matchSchemaType.isEmpty()) {
      throw new IllegalArgumentException(
          String.format("Unexpected jsonSchemaType - %s and jsonSchemaAirbyteType - %s", jsonSchemaType, jsonSchemaAirbyteType));
    } else if (matchSchemaType.size() > 1) {
      throw new RuntimeException(
          String.format("Match with more than one json type! Matched types : %s, Inputs jsonSchemaType : %s, jsonSchemaAirbyteType : %s",
              matchSchemaType, jsonSchemaType, jsonSchemaAirbyteType));
    } else {
      return matchSchemaType.get(0);
    }
  }

  public String getJsonSchemaType() {
    return jsonSchemaType;
  }

  public Schema.Type getAvroType() {
    return avroType;
  }

  @Override
  public String toString() {
    return jsonSchemaType;
  }

  public String getJsonSchemaAirbyteType() {
    return jsonSchemaAirbyteType;
  }

}
