/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.schema.ColumnNameResolver
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.catalog.GlueTableIdGenerator
import io.airbyte.integrations.destination.s3_data_lake.spec.S3DataLakeConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class S3DataLakeTableSchemaMapperTest {

    private fun mapper(
        lowercaseColumnNames: Boolean,
        tableIdGenerator: TableIdGenerator = SimpleTableIdGenerator("default_ns"),
    ): S3DataLakeTableSchemaMapper {
        val config: S3DataLakeConfiguration = mockk {
            every { this@mockk.lowercaseColumnNames } returns lowercaseColumnNames
        }
        return S3DataLakeTableSchemaMapper(
            config,
            tableIdGenerator,
            DefaultTempTableNameGenerator()
        )
    }

    @ParameterizedTest
    @CsvSource(
        "URLs, urls",
        "HTMLParser, htmlparser",
        "projectId, projectid",
        "PROJECT_ID, project_id",
        "Foo.Bar, foo.bar",
        "field_name_with_operator+1, field_name_with_operator+1",
        "field_with_spécial_character, field_with_spécial_character",
        "1field_with_a_leading_number, 1field_with_a_leading_number",
        "already_lowercase, already_lowercase",
        "_airbyte_raw_id, _airbyte_raw_id",
    )
    fun `lowercases column names and changes nothing else when enabled`(
        input: String,
        expected: String,
    ) {
        assertEquals(expected, mapper(lowercaseColumnNames = true).toColumnName(input))
    }

    @ParameterizedTest
    @CsvSource("URLs", "projectId", "Foo.Bar", "field_name_with_operator+1", "my-column")
    fun `passes column names through unchanged when disabled`(input: String) {
        assertEquals(input, mapper(lowercaseColumnNames = false).toColumnName(input))
    }

    @Test
    fun `column names that only differ by case are made unique by the CDK resolver`() {
        val resolver = ColumnNameResolver(mapper(lowercaseColumnNames = true))
        val mapping = resolver.getColumnNameMapping(linkedSetOf("ID", "id", "Id"))
        assertEquals(mapOf("ID" to "id", "id" to "id_1", "Id" to "id_2"), mapping)
    }

    @Test
    fun `final table name mirrors the Glue table id generator`() {
        val mapper =
            mapper(lowercaseColumnNames = true, tableIdGenerator = GlueTableIdGenerator("Db"))
        assertEquals(
            TableName("my_namespace", "my_table"),
            mapper.toFinalTableName(DestinationStream.Descriptor("My-Namespace", "My-Table")),
        )
        assertEquals(
            TableName("db", "my_table"),
            mapper.toFinalTableName(DestinationStream.Descriptor(null, "My-Table")),
        )
    }

    @Test
    fun `final table name mirrors the simple table id generator for other catalogs`() {
        val mapper = mapper(lowercaseColumnNames = true)
        assertEquals(
            TableName("My-Namespace", "My-Table"),
            mapper.toFinalTableName(DestinationStream.Descriptor("My-Namespace", "My-Table")),
        )
        assertEquals(
            TableName("default_ns", "My-Table"),
            mapper.toFinalTableName(DestinationStream.Descriptor(null, "My-Table")),
        )
    }

    @Test
    fun `temp table name comes from the temp table name generator`() {
        val finalTableName = TableName("ns", "table")
        assertEquals(
            DefaultTempTableNameGenerator().generate(finalTableName),
            mapper(lowercaseColumnNames = false).toTempTableName(finalTableName),
        )
    }

    @Test
    fun `column type passes through the airbyte type`() {
        val columnType =
            mapper(lowercaseColumnNames = true)
                .toColumnType(FieldType(IntegerType, nullable = false))
        assertEquals(IntegerType.toString(), columnType.type)
        assertEquals(false, columnType.nullable)
    }
}
