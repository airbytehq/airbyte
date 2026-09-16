/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.ConfigErrorException
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
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class S3DataLakeTableSchemaMapperTest {

    private fun mapper(
        normalizeColumnNames: Boolean,
        tableIdGenerator: TableIdGenerator = SimpleTableIdGenerator("default_ns"),
    ): S3DataLakeTableSchemaMapper {
        val config: S3DataLakeConfiguration = mockk {
            every { this@mockk.normalizeColumnNames } returns normalizeColumnNames
        }
        return S3DataLakeTableSchemaMapper(
            config,
            tableIdGenerator,
            DefaultTempTableNameGenerator()
        )
    }

    @ParameterizedTest
    @CsvSource(
        // lowercase
        "URLs, urls",
        "HTMLParser, htmlparser",
        "projectId, projectid",
        "PROJECT_ID, project_id",
        "already_lowercase, already_lowercase",
        // non-alphanumeric characters become underscores, accents are stripped
        "Foo.Bar, foo_bar",
        "my-column, my_column",
        "'my column', my_column",
        "field_name_with_operator+1, field_name_with_operator_1",
        "field_with_spécial_character, field_with_special_character",
        "'a\"quoted\"name', a_quoted_name",
        "'\${weird}', __weird_",
        "1field_with_a_leading_number, 1field_with_a_leading_number",
        "_airbyte_raw_id, _airbyte_raw_id",
        // SQL reserved keywords get an underscore prefix
        "CURRENT_DATE, _current_date",
        "constraint, _constraint",
        "Current.Timestamp, _current_timestamp",
        "current_date_1, current_date_1",
    )
    fun `normalizes column names when enabled`(input: String, expected: String) {
        assertEquals(expected, mapper(normalizeColumnNames = true).toColumnName(input))
    }

    @Test
    fun `rejects an empty column name when enabled`() {
        assertFailsWith<ConfigErrorException> {
            mapper(normalizeColumnNames = true).toColumnName("")
        }
    }

    @ParameterizedTest
    @CsvSource(
        "URLs",
        "projectId",
        "Foo.Bar",
        "field_name_with_operator+1",
        "my-column",
        "CURRENT_DATE",
        "''",
    )
    fun `passes column names through unchanged when disabled`(input: String) {
        assertEquals(input, mapper(normalizeColumnNames = false).toColumnName(input))
    }

    @Test
    fun `column names that normalize to the same value are made unique by the CDK resolver`() {
        val resolver = ColumnNameResolver(mapper(normalizeColumnNames = true))
        assertEquals(
            mapOf("ID" to "id", "id" to "id_1", "Id" to "id_2"),
            resolver.getColumnNameMapping(linkedSetOf("ID", "id", "Id")),
        )
        assertEquals(
            mapOf("Foo.Bar" to "foo_bar", "foo_bar" to "foo_bar_1", "FOO-BAR" to "foo_bar_2"),
            resolver.getColumnNameMapping(linkedSetOf("Foo.Bar", "foo_bar", "FOO-BAR")),
        )
    }

    @Test
    fun `final table name mirrors the Glue table id generator`() {
        val mapper =
            mapper(normalizeColumnNames = true, tableIdGenerator = GlueTableIdGenerator("Db"))
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
        val mapper = mapper(normalizeColumnNames = true)
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
            mapper(normalizeColumnNames = false).toTempTableName(finalTableName),
        )
    }

    @Test
    fun `column type passes through the airbyte type`() {
        val columnType =
            mapper(normalizeColumnNames = true)
                .toColumnType(FieldType(IntegerType, nullable = false))
        assertEquals(IntegerType.toString(), columnType.type)
        assertEquals(false, columnType.nullable)
    }
}
