/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class SnowflakeSourceOperationsTest {

    private val operations = SnowflakeSourceOperations()

    private fun fieldType(typeName: String, scale: Int? = null): FieldType =
        operations.toFieldType(
            JdbcMetadataQuerier.ColumnMetadata(
                name = "c",
                label = "c",
                type =
                    SystemType(typeName = typeName, typeCode = 0, precision = null, scale = scale),
                nullable = true,
            )
        )

    @Test
    fun `TIME maps to the Snowflake time type that survives the driver`() {
        assertEquals(SnowflakeLocalTimeFieldType, fieldType("TIME"))
    }

    @Test
    fun `timestamp type names from both metadata APIs map to the same types`() {
        // DatabaseMetaData.getColumns reports TIMESTAMP_NTZ, ResultSetMetaData reports
        // TIMESTAMPNTZ.
        assertEquals(SnowflakeLocalDateTimeFieldType, fieldType("TIMESTAMP_NTZ"))
        assertEquals(SnowflakeLocalDateTimeFieldType, fieldType("TIMESTAMPNTZ"))
        assertEquals(SnowflakeLocalDateTimeFieldType, fieldType("DATETIME"))
        assertEquals(SnowflakeOffsetDateTimeFieldType, fieldType("TIMESTAMP_TZ"))
        assertEquals(SnowflakeOffsetDateTimeFieldType, fieldType("TIMESTAMPLTZ"))
    }

    @Test
    fun `other native types`() {
        assertEquals(BigDecimalFieldType, fieldType("NUMBER", scale = 0))
        assertEquals(BigDecimalFieldType, fieldType("NUMBER", scale = 10))
        assertEquals(BooleanFieldType, fieldType("BOOLEAN"))
        assertEquals(LocalDateFieldType, fieldType("DATE"))
        assertEquals(BytesFieldType, fieldType("BINARY"))
        assertEquals(StringFieldType, fieldType("VARIANT"))
        assertEquals(StringFieldType, fieldType("VECTOR"))
        assertEquals(PokemonFieldType, fieldType("SOMETHING_NEW"))
    }
}
