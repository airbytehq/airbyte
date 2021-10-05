/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.StandardSQLTypeName;

/**
 * Mapping of JsonSchema formats to BigQuery Standard SQL types.
 */
public enum JsonSchemaFormat {

  DATE("date", StandardSQLTypeName.DATE),
  DATETIME("date-time", StandardSQLTypeName.DATETIME),
  TIME("time", StandardSQLTypeName.TIME);

  private final String jsonSchemaFormat;
  private final StandardSQLTypeName bigQueryType;

  JsonSchemaFormat(String jsonSchemaFormat, StandardSQLTypeName bigQueryType) {
    this.jsonSchemaFormat = jsonSchemaFormat;
    this.bigQueryType = bigQueryType;
  }

  public static JsonSchemaFormat fromJsonSchemaFormat(String value) {
    for (JsonSchemaFormat type : values()) {
      if (value.equals(type.jsonSchemaFormat)) {
        return type;
      }
    }
    return null;
  }

  public String getJsonSchemaFormat() {
    return jsonSchemaFormat;
  }

  public StandardSQLTypeName getBigQueryType() {
    return bigQueryType;
  }

  @Override
  public String toString() {
    return jsonSchemaFormat;
  }

}
