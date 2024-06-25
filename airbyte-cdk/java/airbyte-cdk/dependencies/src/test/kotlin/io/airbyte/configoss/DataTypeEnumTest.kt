/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class DataTypeEnumTest {
    // We use JsonSchemaPrimitive in tests to construct schemas. We want to verify that their are
    // valid
    // conversions between JsonSchemaPrimitive to DataType so that if anything changes we won't have
    // hard-to-decipher errors in our tests. Once we get rid of Schema, we can can drop this test.
    @Test
    fun testConversionFromJsonSchemaPrimitiveToDataType() {
        Assertions.assertEquals(5, DataType::class.java.enumConstants.size)
        Assertions.assertEquals(
            17,
            JsonSchemaPrimitiveUtil.JsonSchemaPrimitive::class.java.enumConstants.size
        )

        Assertions.assertEquals(
            DataType.STRING,
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.STRING.toString()
                    .lowercase(Locale.getDefault())
            )
        )
        Assertions.assertEquals(
            DataType.NUMBER,
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NUMBER.toString()
                    .lowercase(Locale.getDefault())
            )
        )
        Assertions.assertEquals(
            DataType.BOOLEAN,
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.BOOLEAN.toString()
                    .lowercase(Locale.getDefault())
            )
        )
        Assertions.assertEquals(
            DataType.ARRAY,
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.ARRAY.toString()
                    .lowercase(Locale.getDefault())
            )
        )
        Assertions.assertEquals(
            DataType.OBJECT,
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.OBJECT.toString()
                    .lowercase(Locale.getDefault())
            )
        )
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            DataType.fromValue(
                JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.NULL.toString()
                    .lowercase(Locale.getDefault())
            )
        }
    }
}
