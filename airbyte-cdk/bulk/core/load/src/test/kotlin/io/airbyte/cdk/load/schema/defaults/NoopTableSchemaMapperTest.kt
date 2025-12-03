/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.defaults

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.TableName
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class NoopTableSchemaMapperTest {
    private val mapper = NoopTableSchemaMapper()

    @Test
    fun `toFinalTableName returns unchanged table name`() {
        val desc1 = DestinationStream.Descriptor("namespace", "name")
        val result1 = mapper.toFinalTableName(desc1)
        Assertions.assertEquals(TableName("namespace", "name"), result1)

        val desc2 = DestinationStream.Descriptor(null, "name")
        val result2 = mapper.toFinalTableName(desc2)
        Assertions.assertEquals(TableName("", "name"), result2)
    }

    @Test
    fun `toTempTableName returns unchanged table name`() {
        val tableName = TableName("namespace", "name")
        val result = mapper.toTempTableName(tableName)
        Assertions.assertEquals(tableName, result)
    }

    @Test
    fun `toColumnName returns unchanged column name`() {
        Assertions.assertEquals("column_name", mapper.toColumnName("column_name"))
        Assertions.assertEquals("UPPERCASE", mapper.toColumnName("UPPERCASE"))
        Assertions.assertEquals("123_numbers", mapper.toColumnName("123_numbers"))
        Assertions.assertEquals("special@#chars", mapper.toColumnName("special@#chars"))
        Assertions.assertEquals("", mapper.toColumnName(""))
    }

    @ParameterizedTest
    @MethodSource("fieldTypeTestCases")
    fun `toColumnType maps field types as strings`(
        fieldType: FieldType,
    ) {
        val result = mapper.toColumnType(fieldType)
        Assertions.assertEquals(ColumnType(fieldType.type.toString(), fieldType.nullable), result)
    }

    @Test
    fun `handles empty and special cases`() {
        val emptyDesc = DestinationStream.Descriptor("", "")
        Assertions.assertEquals(TableName("", ""), mapper.toFinalTableName(emptyDesc))

        val emptyTable = TableName("", "")
        Assertions.assertEquals(emptyTable, mapper.toTempTableName(emptyTable))

        Assertions.assertEquals("", mapper.toColumnName(""))
    }

    companion object {
        @JvmStatic
        fun fieldTypeTestCases(): Stream<Arguments> =
            Stream.of(
                Arguments.of(FieldType(StringType, false)),
                Arguments.of(FieldType(IntegerType, false)),
                Arguments.of(FieldType(BooleanType, true)),
                Arguments.of(FieldType(NumberType, false)),
            )
    }
}
