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

  STRING("string", true, null, Schema.Type.STRING),
  NUMBER_INT("number", true, "integer", Schema.Type.INT),
  NUMBER_BIGINT("string", true, "big_integer", Schema.Type.STRING),
  NUMBER_FLOAT("number", true, "float", Schema.Type.FLOAT),
  NUMBER("number", true, null, Schema.Type.DOUBLE),
  INTEGER("integer", true, null, Schema.Type.INT),
  BOOLEAN("boolean", true, null, Schema.Type.BOOLEAN),
  NULL("null", true, null, Schema.Type.NULL),
  OBJECT("object", false, null, Schema.Type.RECORD),
  ARRAY("array", false, null, Schema.Type.ARRAY),
  COMBINED("combined", false, null, Schema.Type.UNION);

  private final String jsonSchemaType;
  private final boolean isPrimitive;
  private final Schema.Type avroType;
  private final String jsonSchemaAirbyteType;

  JsonSchemaType(final String jsonSchemaType, final boolean isPrimitive, final String jsonSchemaAirbyteType, final Schema.Type avroType) {
    this.jsonSchemaType = jsonSchemaType;
    this.jsonSchemaAirbyteType = jsonSchemaAirbyteType;
    this.isPrimitive = isPrimitive;
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

  public boolean isPrimitive() {
    return isPrimitive;
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
