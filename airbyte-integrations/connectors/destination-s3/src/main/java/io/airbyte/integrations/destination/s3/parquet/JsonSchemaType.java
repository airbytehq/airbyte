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
