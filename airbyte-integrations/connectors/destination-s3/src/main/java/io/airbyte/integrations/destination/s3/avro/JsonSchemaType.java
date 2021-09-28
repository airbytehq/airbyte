/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import org.apache.avro.Schema;

/**
 * Mapping of JsonSchema types to Avro types.
 */
public enum JsonSchemaType {

  STRING("string", true, Schema.Type.STRING),
  NUMBER("number", true, Schema.Type.DOUBLE),
  INTEGER("integer", true, Schema.Type.INT),
  BOOLEAN("boolean", true, Schema.Type.BOOLEAN),
  NULL("null", true, Schema.Type.NULL),
  OBJECT("object", false, Schema.Type.RECORD),
  ARRAY("array", false, Schema.Type.ARRAY),
  COMBINED("combined", false, Schema.Type.UNION);

  private final String jsonSchemaType;
  private final boolean isPrimitive;
  private final Schema.Type avroType;

  JsonSchemaType(String jsonSchemaType, boolean isPrimitive, Schema.Type avroType) {
    this.jsonSchemaType = jsonSchemaType;
    this.isPrimitive = isPrimitive;
    this.avroType = avroType;
  }

  public static JsonSchemaType fromJsonSchemaType(String value) {
    for (JsonSchemaType type : values()) {
      if (value.equals(type.jsonSchemaType)) {
        return type;
      }
    }
    throw new IllegalArgumentException("Unexpected json schema type: " + value);
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

}
