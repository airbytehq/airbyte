/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class SnowflakeSourceOperationsTest {

    private val ops = SnowflakeSourceOperations()

    private fun columnMetadata(
        typeName: String?,
        typeCode: Int = java.sql.Types.OTHER,
        precision: Int? = null,
        scale: Int? = null,
    ): ColumnMetadata =
        ColumnMetadata(
            name = "test_col",
            label = "test_col",
            type = SystemType(typeName = typeName, typeCode = typeCode, precision = precision, scale = scale),
            nullable = true,
        )

    /**
     * Verifies that all Snowflake numeric type aliases (NUMBER, DECIMAL, NUMERIC, INT, INTEGER,
     * BIGINT, SMALLINT, TINYINT, BYTEINT) produce the same [LeafAirbyteSchemaType] when they
     * share the same scale value. This prevents the type mismatch that caused streams to be
     * silently dropped when the Snowflake JDBC driver returned different type name strings
     * for the same column via different metadata APIs.
     *
     * See: https://github.com/airbytehq/airbyte/issues/74064
     */
    @ParameterizedTest
    @CsvSource(
        "NUMBER", "DECIMAL", "NUMERIC", "INT", "INTEGER",
        "BIGINT", "SMALLINT", "TINYINT", "BYTEINT"
    )
    fun `all numeric type aliases with scale 0 map to INTEGER`(typeName: String) {
        val fieldType = ops.toFieldType(columnMetadata(typeName, precision = 38, scale = 0))
        assertSame(BigIntegerFieldType, fieldType)
        assertEquals(LeafAirbyteSchemaType.INTEGER, fieldType.airbyteSchemaType)
    }

    @ParameterizedTest
    @CsvSource(
        "NUMBER", "DECIMAL", "NUMERIC", "INT", "INTEGER",
        "BIGINT", "SMALLINT", "TINYINT", "BYTEINT"
    )
    fun `all numeric type aliases with scale greater than 0 map to NUMBER`(typeName: String) {
        val fieldType = ops.toFieldType(columnMetadata(typeName, precision = 38, scale = 6))
        assertSame(BigDecimalFieldType, fieldType)
        assertEquals(LeafAirbyteSchemaType.NUMBER, fieldType.airbyteSchemaType)
    }

    @ParameterizedTest
    @CsvSource(
        "NUMBER", "DECIMAL", "NUMERIC", "INT", "INTEGER",
        "BIGINT", "SMALLINT", "TINYINT", "BYTEINT"
    )
    fun `all numeric type aliases with null scale map to INTEGER`(typeName: String) {
        val fieldType = ops.toFieldType(columnMetadata(typeName, precision = 38, scale = null))
        assertSame(BigIntegerFieldType, fieldType)
        assertEquals(LeafAirbyteSchemaType.INTEGER, fieldType.airbyteSchemaType)
    }

    @Test
    fun `NUMBER and INTEGER produce same type for NUMBER 38 0 column`() {
        // This is the exact scenario from the reported bug:
        // DatabaseMetaData.getColumns() returns "NUMBER" while
        // ResultSetMetaData.getColumnTypeName() returns "INTEGER" for NUMBER(38,0).
        val fromDbMetadata = ops.toFieldType(columnMetadata("NUMBER", precision = 38, scale = 0))
        val fromRsMetadata = ops.toFieldType(columnMetadata("INTEGER", precision = 38, scale = 0))
        assertSame(fromDbMetadata, fromRsMetadata)
    }

    @Test
    fun `non-numeric types are not affected by scale normalization`() {
        assertEquals(StringFieldType, ops.toFieldType(columnMetadata("VARCHAR")))
        assertEquals(StringFieldType, ops.toFieldType(columnMetadata("TEXT")))
        assertEquals(BooleanFieldType, ops.toFieldType(columnMetadata("BOOLEAN")))
        assertEquals(DoubleFieldType, ops.toFieldType(columnMetadata("FLOAT")))
        assertEquals(DoubleFieldType, ops.toFieldType(columnMetadata("DOUBLE")))
        assertEquals(LocalDateFieldType, ops.toFieldType(columnMetadata("DATE")))
        assertEquals(LocalTimeFieldType, ops.toFieldType(columnMetadata("TIME")))
        assertEquals(LocalDateTimeFieldType, ops.toFieldType(columnMetadata("TIMESTAMP_NTZ")))
        assertEquals(BytesFieldType, ops.toFieldType(columnMetadata("BINARY")))
        assertEquals(StringFieldType, ops.toFieldType(columnMetadata("VARIANT")))
        assertEquals(StringFieldType, ops.toFieldType(columnMetadata("ARRAY")))
        assertEquals(PokemonFieldType, ops.toFieldType(columnMetadata("UNKNOWN_TYPE")))
    }

    @Test
    fun `case insensitivity for type names`() {
        val lower = ops.toFieldType(columnMetadata("number", precision = 10, scale = 2))
        val upper = ops.toFieldType(columnMetadata("NUMBER", precision = 10, scale = 2))
        val mixed = ops.toFieldType(columnMetadata("Number", precision = 10, scale = 2))
        assertSame(lower, upper)
        assertSame(upper, mixed)
    }
}
