package io.airbyte.integrations.destination.s3.parquet;

import org.apache.avro.Schema;

/**
 * Mapping of JsonSchema types to Avro types.
 */
public enum JsonSchemaType {

  STRING("string", Schema.Type.STRING),
  NUMBER("number", Schema.Type.DOUBLE),
  INTEGER("integer", Schema.Type.INT),
  BOOLEAN("boolean", Schema.Type.BOOLEAN),
  NULL("null", Schema.Type.NULL),
  OBJECT("object", Schema.Type.RECORD),
  ARRAY("array", Schema.Type.ARRAY);

  private final String jsonSchemaType;
  private final Schema.Type avroType;

  JsonSchemaType(String jsonSchemaType, Schema.Type avroType) {
    this.jsonSchemaType = jsonSchemaType;
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

  public Schema.Type getAvroType() {
    return avroType;
  }

  @Override
  public String toString() {
    return jsonSchemaType;
  }

}
