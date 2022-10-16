/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.StandardSQLTypeName;

/**
 * Mapping of JsonSchema types to BigQuery Standard SQL types.
 *
 * The order field of the enum provides us the ability to sort union types (array of JsonSchemaType
 * from narrow to wider scopes of types. For example, STRING takes precedence over NUMBER if both
 * are included in the same type array.
 */
public enum JsonSchemaType {

  STRING(0, "string", StandardSQLTypeName.STRING),
  NUMBER(1, "number", StandardSQLTypeName.FLOAT64),
  INTEGER(2, "integer", StandardSQLTypeName.INT64),
  BOOLEAN(3, "boolean", StandardSQLTypeName.BOOL),
  OBJECT(4, "object", StandardSQLTypeName.STRUCT),
  ARRAY(5, "array", StandardSQLTypeName.ARRAY),
  NULL(6, "null", null);

  private final int order;
  private final String jsonSchemaType;
  private final StandardSQLTypeName bigQueryType;

  JsonSchemaType(final int order, final String jsonSchemaType, final StandardSQLTypeName bigQueryType) {
    this.order = order;
    this.jsonSchemaType = jsonSchemaType;
    this.bigQueryType = bigQueryType;
  }

  public static JsonSchemaType fromJsonSchemaType(final String value) {
    for (final JsonSchemaType type : values()) {
      if (value.equals(type.jsonSchemaType)) {
        return type;
      }
    }
    throw new IllegalArgumentException("Unexpected json schema type: " + value);
  }

  public int getOrder() {
    return order;
  }

  public String getJsonSchemaType() {
    return jsonSchemaType;
  }

  public StandardSQLTypeName getBigQueryType() {
    return bigQueryType;
  }

  @Override
  public String toString() {
    return jsonSchemaType;
  }

}
