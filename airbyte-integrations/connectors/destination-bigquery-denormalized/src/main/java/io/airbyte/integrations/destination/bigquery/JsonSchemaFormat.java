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
