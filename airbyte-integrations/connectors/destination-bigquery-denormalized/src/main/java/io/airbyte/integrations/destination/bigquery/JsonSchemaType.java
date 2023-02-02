/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.StandardSQLTypeName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Mapping of JsonSchema types to BigQuery Standard SQL types.
 *
 * The order field of the enum provides us the ability to sort union types (array of JsonSchemaType
 * from narrow to wider scopes of types. For example, STRING takes precedence over NUMBER if both
 * are included in the same type array.
 */
public enum JsonSchemaType {

  STRING(0, "WellKnownTypes.json#/definitions/String", StandardSQLTypeName.STRING),
  NUMBER(1, "WellKnownTypes.json#/definitions/Number", StandardSQLTypeName.FLOAT64),
  INTEGER(2, "WellKnownTypes.json#/definitions/Integer", StandardSQLTypeName.INT64),
  BOOLEAN(3, "WellKnownTypes.json#/definitions/Boolean", StandardSQLTypeName.BOOL),
  DATE(4, "WellKnownTypes.json#/definitions/Date", StandardSQLTypeName.DATE),
  TIMESTAMP_WITHOUT_TIMEZONE(5, "WellKnownTypes.json#/definitions/TimestampWithoutTimezone", StandardSQLTypeName.DATETIME),
  TIMESTAMP_WITH_TIMEZONE(6, "WellKnownTypes.json#/definitions/TimestampWithTimezone", StandardSQLTypeName.TIMESTAMP),
  TIME_WITHOUT_TIMEZONE(7, "WellKnownTypes.json#/definitions/TimeWithoutTimezone", StandardSQLTypeName.TIME),
  TIME_WITH_TIMEZONE(8, "WellKnownTypes.json#/definitions/TimeWithTimezone", StandardSQLTypeName.STRING),
  BINARY_DATA(9, "WellKnownTypes.json#/definitions/BinaryData", StandardSQLTypeName.BYTES),
  OBJECT(10, "object", StandardSQLTypeName.STRUCT),
  ARRAY(11, "array", StandardSQLTypeName.ARRAY),
  NULL(12, "null", null);

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonSchemaType.class);
  private final int order;
  private final String jsonSchemaType;
  private final StandardSQLTypeName bigQueryType;

  JsonSchemaType(final int order, final String jsonSchemaType, final StandardSQLTypeName bigQueryType) {
    this.order = order;
    this.jsonSchemaType = jsonSchemaType;
    this.bigQueryType = bigQueryType;
  }

  public static JsonSchemaType fromJsonSchemaType(String fieldName, final String value) {
    for (final JsonSchemaType type : values()) {
      if (value.equals(type.jsonSchemaType)) {
        return type;
      }
    }
    LOGGER.warn("Field {} has no type defined, defaulting to STRING", fieldName);
    return JsonSchemaType.STRING;
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
