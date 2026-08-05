/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.integrations.destination.snowflake.spec.NumberDataType
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDataType
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Tests that [NumberType] is mapped to FLOAT or NUMERIC(38,9) based on the number_data_type option,
 * and that [IntegerType] maps to NUMBER regardless of it.
 */
internal class SnowflakeTableSchemaMapperTest {

    private fun mapper(mode: NumberDataType) =
        SnowflakeTableSchemaMapper(
            config = mockk { every { numberDataTypeConversion } returns mode },
            tempTableNameGenerator = mockk(),
        )

    @Test
    fun testNumberTypeMapsToFloatInFloatMode() {
        val columnType =
            mapper(NumberDataType.FLOAT).toColumnType(FieldType(NumberType, nullable = true))
        assertEquals(SnowflakeDataType.FLOAT.typeName, columnType.type)
    }

    @Test
    fun testNumberTypeMapsToNumericInNumberMode() {
        val columnType =
            mapper(NumberDataType.NUMBER_38_9).toColumnType(FieldType(NumberType, nullable = true))
        assertEquals(SnowflakeDataType.NUMERIC_38_9.typeName, columnType.type)
    }

    @Test
    fun testIntegerTypeMapsToNumberInBothModes() {
        NumberDataType.entries.forEach { mode ->
            val columnType = mapper(mode).toColumnType(FieldType(IntegerType, nullable = true))
            assertEquals(SnowflakeDataType.NUMBER.typeName, columnType.type)
        }
    }
}
