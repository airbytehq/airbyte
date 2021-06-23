/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

  JsonSchemaType(int order, String jsonSchemaType, StandardSQLTypeName bigQueryType) {
    this.order = order;
    this.jsonSchemaType = jsonSchemaType;
    this.bigQueryType = bigQueryType;
  }

  public static JsonSchemaType fromJsonSchemaType(String value) {
    for (JsonSchemaType type : values()) {
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
