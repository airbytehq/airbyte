/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import org.junit.jupiter.api.Test;

class DataTypeEnumTest {

  // We use JsonSchemaPrimitive in tests to construct schemas. We want to verify that their are valid
  // conversions between JsonSchemaPrimitive to DataType so that if anything changes we won't have
  // hard-to-decipher errors in our tests. Once we get rid of Schema, we can can drop this test.
  @Test
  void testConversionFromJsonSchemaPrimitiveToDataType() {
    assertEquals(5, DataType.class.getEnumConstants().length);
    assertEquals(17, JsonSchemaPrimitive.class.getEnumConstants().length);

    assertEquals(DataType.STRING, DataType.fromValue(JsonSchemaPrimitive.STRING.toString().toLowerCase()));
    assertEquals(DataType.NUMBER, DataType.fromValue(JsonSchemaPrimitive.NUMBER.toString().toLowerCase()));
    assertEquals(DataType.BOOLEAN, DataType.fromValue(JsonSchemaPrimitive.BOOLEAN.toString().toLowerCase()));
    assertEquals(DataType.ARRAY, DataType.fromValue(JsonSchemaPrimitive.ARRAY.toString().toLowerCase()));
    assertEquals(DataType.OBJECT, DataType.fromValue(JsonSchemaPrimitive.OBJECT.toString().toLowerCase()));
    assertThrows(IllegalArgumentException.class, () -> DataType.fromValue(JsonSchemaPrimitive.NULL.toString().toLowerCase()));
  }

}
