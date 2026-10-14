/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.schema

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.sql.RedshiftDataType
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class RedshiftTableSchemaMapperTest {

    private lateinit var config: RedshiftConfiguration
    private lateinit var tempTableNameGenerator: TempTableNameGenerator
    private lateinit var mapper: RedshiftTableSchemaMapper

    @BeforeEach
    fun setup() {
        config = mockk()
        every { config.schema } returns "public"

        tempTableNameGenerator = mockk()
        mapper = RedshiftTableSchemaMapper(config, tempTableNameGenerator)
    }

    // ================================================================
    // toFinalTableName
    // ================================================================

    @Test
    fun `toFinalTableName maps namespace and name with lowercasing`() {
        val desc = DestinationStream.Descriptor(namespace = "MySchema", name = "MyTable")

        val result = mapper.toFinalTableName(desc)

        assertEquals("myschema", result.namespace)
        assertEquals("mytable", result.name)
    }

    @Test
    fun `toFinalTableName sanitizes special characters`() {
        val desc = DestinationStream.Descriptor(namespace = "my-schema", name = "my.table")

        val result = mapper.toFinalTableName(desc)

        assertEquals("my_schema", result.namespace)
        assertEquals("my_table", result.name)
    }

    @Test
    fun `toFinalTableName uses config schema when descriptor namespace is null`() {
        every { config.schema } returns "default_schema"
        val desc = DestinationStream.Descriptor(namespace = null, name = "my_table")

        val result = mapper.toFinalTableName(desc)

        assertEquals("default_schema", result.namespace)
        assertEquals("my_table", result.name)
    }

    // ================================================================
    // toTempTableName
    // ================================================================

    @Test
    fun `toTempTableName delegates to TempTableNameGenerator`() {
        val tableName = TableName(namespace = "public", name = "my_table")
        val expectedTemp = TableName(namespace = "public", name = "tmp_my_table_abc123")
        every { tempTableNameGenerator.generate(tableName) } returns expectedTemp

        val result = mapper.toTempTableName(tableName)

        assertEquals(expectedTemp, result)
        verify { tempTableNameGenerator.generate(tableName) }
    }

    // ================================================================
    // toColumnName
    // ================================================================

    @Test
    fun `toColumnName applies naming transformation`() {
        assertEquals("my_column", mapper.toColumnName("my_column"))
        assertEquals("my_column", mapper.toColumnName("My-Column"))
        assertEquals("_1col", mapper.toColumnName("1col"))
    }

    // ================================================================
    // toColumnType
    // ================================================================

    @ParameterizedTest(name = "{0} -> {1}")
    @MethodSource("typeMapping")
    fun `toColumnType maps all Airbyte types correctly`(
        fieldType: FieldType,
        expectedTypeName: String,
    ) {
        val result = mapper.toColumnType(fieldType)

        assertEquals(expectedTypeName, result.type)
        assertEquals(fieldType.nullable, result.nullable)
    }

    // ================================================================
    // toFinalSchema
    // ================================================================

    @Test
    fun `toFinalSchema returns schema unchanged`() {
        val tableName = TableName(namespace = "public", name = "test")
        val tableSchema =
            StreamTableSchema(
                tableNames = TableNames(finalTableName = tableName, tempTableName = tableName),
                columnSchema =
                    ColumnSchema(
                        inputToFinalColumnNames = mapOf("col" to "col"),
                        finalSchema =
                            mapOf("col" to ColumnType(RedshiftDataType.VARCHAR.typeName, false)),
                        inputSchema = emptyMap(),
                    ),
                importType = Append,
            )

        val result = mapper.toFinalSchema(tableSchema)

        assertEquals(tableSchema, result)
    }

    // ================================================================
    // colsConflict
    // ================================================================

    @Test
    fun `colsConflict is case-insensitive`() {
        assertTrue(mapper.colsConflict("MyColumn", "mycolumn"))
        assertTrue(mapper.colsConflict("ABC", "abc"))
        assertFalse(mapper.colsConflict("col_a", "col_b"))
    }

    companion object {
        @JvmStatic
        fun typeMapping() =
            listOf(
                // Simple types
                Arguments.of(FieldType(BooleanType, false), "boolean"),
                Arguments.of(FieldType(IntegerType, true), "bigint"),
                Arguments.of(FieldType(NumberType, false), "decimal(38,9)"),
                Arguments.of(FieldType(StringType, true), "varchar(65535)"),
                // Temporal types
                Arguments.of(FieldType(DateType, false), "date"),
                Arguments.of(FieldType(TimeTypeWithTimezone, false), "timetz"),
                Arguments.of(FieldType(TimeTypeWithoutTimezone, true), "time"),
                Arguments.of(FieldType(TimestampTypeWithTimezone, false), "timestamptz"),
                Arguments.of(FieldType(TimestampTypeWithoutTimezone, true), "timestamp"),
                // Semi-structured types -> SUPER
                Arguments.of(
                    FieldType(ArrayType(FieldType(StringType, true)), false),
                    "super",
                ),
                Arguments.of(FieldType(ArrayTypeWithoutSchema, true), "super"),
                Arguments.of(
                    FieldType(
                        ObjectType(linkedMapOf("k" to FieldType(StringType, true))),
                        false,
                    ),
                    "super",
                ),
                Arguments.of(FieldType(ObjectTypeWithEmptySchema, true), "super"),
                Arguments.of(FieldType(ObjectTypeWithoutSchema, false), "super"),
                Arguments.of(
                    FieldType(
                        UnionType(setOf(StringType, IntegerType), isLegacyUnion = false),
                        true,
                    ),
                    "varchar(65535)",
                ),
                Arguments.of(
                    FieldType(
                        UnknownType(com.fasterxml.jackson.databind.node.NullNode.instance),
                        false,
                    ),
                    "varchar(65535)",
                ),
            )
    }
}
