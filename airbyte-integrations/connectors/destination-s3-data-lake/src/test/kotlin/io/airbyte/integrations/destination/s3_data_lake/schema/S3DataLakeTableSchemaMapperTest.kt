/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class S3DataLakeTableSchemaMapperTest {

    private lateinit var mapper: S3DataLakeTableSchemaMapper
    private lateinit var tempTableNameGenerator: TempTableNameGenerator

    @BeforeEach
    fun setup() {
        tempTableNameGenerator = mockk()
        mapper = S3DataLakeTableSchemaMapper(tempTableNameGenerator)
    }

    @Test
    fun `toColumnName lowercases and sanitizes column names`() {
        assertEquals("my_column", mapper.toColumnName("My_Column"))
        assertEquals("mycolumn", mapper.toColumnName("MyColumn"))
        assertEquals("my_column_name", mapper.toColumnName("My Column Name"))
        assertEquals("column_1", mapper.toColumnName("Column-1"))
        assertEquals("column_with_special__chars", mapper.toColumnName("column_with_special!@chars"))
    }

    @Test
    fun `toColumnName handles already lowercase names`() {
        assertEquals("lowercase", mapper.toColumnName("lowercase"))
        assertEquals("already_lowercase", mapper.toColumnName("already_lowercase"))
    }

    @Test
    fun `toColumnName handles uppercase names`() {
        assertEquals("uppercase", mapper.toColumnName("UPPERCASE"))
        assertEquals("all_upper", mapper.toColumnName("ALL_UPPER"))
    }

    @Test
    fun `toColumnName handles mixed case with special characters`() {
        assertEquals("camelcase", mapper.toColumnName("camelCase"))
        assertEquals("pascalcase", mapper.toColumnName("PascalCase"))
        assertEquals("user_email_address", mapper.toColumnName("User Email Address"))
    }

    @Test
    fun `toFinalTableName lowercases namespace and name`() {
        val desc = DestinationStream.Descriptor("MyNamespace", "MyStream")
        val result = mapper.toFinalTableName(desc)
        assertEquals("mynamespace", result.namespace)
        assertEquals("mystream", result.name)
    }

    @Test
    fun `toFinalTableName sanitizes special characters in namespace and name`() {
        val desc = DestinationStream.Descriptor("My Namespace", "My-Stream")
        val result = mapper.toFinalTableName(desc)
        assertEquals("my_namespace", result.namespace)
        assertEquals("my_stream", result.name)
    }

    @Test
    fun `toFinalTableName handles null namespace`() {
        val desc = DestinationStream.Descriptor(null, "MyStream")
        val result = mapper.toFinalTableName(desc)
        assertEquals("", result.namespace)
        assertEquals("mystream", result.name)
    }

    @Test
    fun `toTempTableName delegates to TempTableNameGenerator`() {
        val tableName = TableName("namespace", "name")
        val expectedTempName = TableName("namespace", "temp_name")
        every { tempTableNameGenerator.generate(tableName) } returns expectedTempName
        val result = mapper.toTempTableName(tableName)
        assertEquals(expectedTempName, result)
    }

    @Test
    fun `toColumnType maps types correctly`() {
        assertEquals("BOOL", mapper.toColumnType(FieldType(BooleanType, nullable = false)).typeName)
        assertEquals("DATE", mapper.toColumnType(FieldType(DateType, nullable = false)).typeName)
        assertEquals("INT64", mapper.toColumnType(FieldType(IntegerType, nullable = false)).typeName)
        assertEquals("FLOAT64", mapper.toColumnType(FieldType(NumberType, nullable = false)).typeName)
        assertEquals("STRING", mapper.toColumnType(FieldType(StringType, nullable = false)).typeName)
        assertEquals(
            "TIMESTAMP",
            mapper.toColumnType(FieldType(TimestampTypeWithTimezone, nullable = false)).typeName
        )
        assertEquals(
            "TIMESTAMP",
            mapper.toColumnType(FieldType(TimestampTypeWithoutTimezone, nullable = false)).typeName
        )
        assertEquals(
            "STRING",
            mapper.toColumnType(FieldType(TimeTypeWithTimezone, nullable = false)).typeName
        )
        assertEquals(
            "STRING",
            mapper.toColumnType(FieldType(TimeTypeWithoutTimezone, nullable = false)).typeName
        )
    }

    @Test
    fun `toColumnType preserves nullability`() {
        val nullableType = mapper.toColumnType(FieldType(StringType, nullable = true))
        assertEquals(true, nullableType.nullable)

        val nonNullableType = mapper.toColumnType(FieldType(StringType, nullable = false))
        assertEquals(false, nonNullableType.nullable)
    }
}
