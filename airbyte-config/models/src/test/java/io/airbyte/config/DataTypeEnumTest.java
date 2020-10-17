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

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import org.junit.jupiter.api.Test;

public class DataTypeEnumTest {

  // We use JsonSchemaPrimitive in tests to construct schemas. We want to verify that their are valid
  // conversions between JsonSchemaPrimitive to DataType so that if anything changes we won't have
  // hard-to-decipher errors in our tests. Once we get rid of Schema, we can can drop this test.
  @Test
  void testConversionFromJsonSchemaPrimitiveToDataType() {
    assertEquals(5, DataType.class.getEnumConstants().length);
    assertEquals(6, JsonSchemaPrimitive.class.getEnumConstants().length);

    assertEquals(DataType.STRING, DataType.fromValue(JsonSchemaPrimitive.STRING.toString().toLowerCase()));
    assertEquals(DataType.NUMBER, DataType.fromValue(JsonSchemaPrimitive.NUMBER.toString().toLowerCase()));
    assertEquals(DataType.BOOLEAN, DataType.fromValue(JsonSchemaPrimitive.BOOLEAN.toString().toLowerCase()));
    assertEquals(DataType.ARRAY, DataType.fromValue(JsonSchemaPrimitive.ARRAY.toString().toLowerCase()));
    assertEquals(DataType.OBJECT, DataType.fromValue(JsonSchemaPrimitive.OBJECT.toString().toLowerCase()));
    assertThrows(IllegalArgumentException.class, () -> DataType.fromValue(JsonSchemaPrimitive.NULL.toString().toLowerCase()));
  }

}
