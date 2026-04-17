/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class S3DataLakeTableSchemaMapperTest {

    private val tempTableNameGenerator: TempTableNameGenerator = mockk()

    // -- GlueTableSchemaMapper with lowercaseColumnNames=true --

    @Test
    fun `Glue mapper converts camelCase columns to snake_case when toggle is enabled`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("project_id", mapper.toColumnName("projectId"))
        assertEquals("project_key", mapper.toColumnName("projectKey"))
        assertEquals("rendered_fields", mapper.toColumnName("renderedFields"))
        assertEquals(
            "versioned_representations",
            mapper.toColumnName("versionedRepresentations"),
        )
    }

    @Test
    fun `Glue mapper sanitizes special characters when toggle is enabled`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("rendered_fields", mapper.toColumnName("rendered-fields"))
        assertEquals("my_column_name", mapper.toColumnName("my.column.name"))
        assertEquals("col_with_spaces", mapper.toColumnName("col with spaces"))
    }

    @Test
    fun `Glue mapper handles mixed camelCase and special characters`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("my_camel_case_col", mapper.toColumnName("My-CamelCase-Col"))
        assertEquals("project_id", mapper.toColumnName("Project.Id"))
    }

    @Test
    fun `Glue mapper transforms all testFunkyCharacters columns correctly`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("field_with_camel_case", mapper.toColumnName("fieldWithCamelCase"))
        assertEquals("proper_case", mapper.toColumnName("ProperCase"))
        assertEquals("field_with_all_caps", mapper.toColumnName("FIELD_WITH_ALL_CAPS"))
        assertEquals("field_with_underscore", mapper.toColumnName("field_with_underscore"))
        assertEquals(
            "field_with_special_character",
            mapper.toColumnName("field_with_spécial_character"),
        )
        assertEquals(
            "field_name_with_operator_1",
            mapper.toColumnName("field_name_with_operator+1"),
        )
        assertEquals(
            "1field_with_a_leading_number",
            mapper.toColumnName("1field_with_a_leading_number"),
        )
        assertEquals("order", mapper.toColumnName("order"))
        assertEquals("foo_bar", mapper.toColumnName("Foo.Bar"))
    }

    @Test
    fun `Glue mapper leaves already lowercase names unchanged when toggle is enabled`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("id", mapper.toColumnName("id"))
        assertEquals("name", mapper.toColumnName("name"))
        assertEquals("_airbyte_raw_id", mapper.toColumnName("_airbyte_raw_id"))
    }

    @Test
    fun `Glue mapper handles consecutive uppercase letters (acronyms)`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("html_parser", mapper.toColumnName("HTMLParser"))
        assertEquals("my_url", mapper.toColumnName("myURL"))
        assertEquals("io_stream", mapper.toColumnName("IOStream"))
        assertEquals("get_http_response", mapper.toColumnName("getHTTPResponse"))
    }

    @Test
    fun `Glue mapper handles SCREAMING_CASE and all-uppercase`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("project_id", mapper.toColumnName("PROJECT_ID"))
        assertEquals("field_with_all_caps", mapper.toColumnName("FIELD_WITH_ALL_CAPS"))
        // All-uppercase with no separators — no word boundaries to detect
        assertEquals("projectid", mapper.toColumnName("PROJECTID"))
    }

    // -- GlueTableSchemaMapper with lowercaseColumnNames=false (default) --

    @Test
    fun `Glue mapper passes column names through when toggle is disabled`() {
        val mapper =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = false)
        assertEquals("projectId", mapper.toColumnName("projectId"))
        assertEquals("renderedFields", mapper.toColumnName("renderedFields"))
        assertEquals("my-column", mapper.toColumnName("my-column"))
    }

    // -- Table name lowercasing always applies for Glue --

    @Test
    fun `Glue mapper always lowercases table names regardless of toggle`() {
        val mapperOff =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = false)
        val mapperOn =
            GlueTableSchemaMapper("testdb", tempTableNameGenerator, lowercaseColumnNames = true)
        val descriptor = DestinationStream.Descriptor("MyNamespace", "MyTable")

        val resultOff = mapperOff.toFinalTableName(descriptor)
        val resultOn = mapperOn.toFinalTableName(descriptor)

        assertEquals("mynamespace", resultOff.namespace)
        assertEquals("mytable", resultOff.name)
        assertEquals("mynamespace", resultOn.namespace)
        assertEquals("mytable", resultOn.name)
    }

    @Test
    fun `Glue mapper sanitizes table names and namespaces`() {
        val mapper = GlueTableSchemaMapper("testdb", tempTableNameGenerator)
        val descriptor = DestinationStream.Descriptor("my-namespace", "my-table")
        val tableName = mapper.toFinalTableName(descriptor)
        assertEquals("my_namespace", tableName.namespace)
        assertEquals("my_table", tableName.name)
    }

    @Test
    fun `Glue mapper uses databaseName as fallback namespace`() {
        val mapper = GlueTableSchemaMapper("FallbackDb", tempTableNameGenerator)
        val descriptor = DestinationStream.Descriptor(null, "MyTable")
        val tableName = mapper.toFinalTableName(descriptor)
        assertEquals("fallbackdb", tableName.namespace)
        assertEquals("mytable", tableName.name)
    }

    // -- S3DataLakeDefaultTableSchemaMapper tests --

    @Test
    fun `Default mapper passes column names through when toggle is disabled`() {
        val mapper =
            S3DataLakeDefaultTableSchemaMapper(tempTableNameGenerator, lowercaseColumnNames = false)
        assertEquals("projectId", mapper.toColumnName("projectId"))
        assertEquals("renderedFields", mapper.toColumnName("renderedFields"))
        assertEquals("my-column", mapper.toColumnName("my-column"))
    }

    @Test
    fun `Default mapper converts camelCase to snake_case when toggle is enabled`() {
        val mapper =
            S3DataLakeDefaultTableSchemaMapper(tempTableNameGenerator, lowercaseColumnNames = true)
        assertEquals("project_id", mapper.toColumnName("projectId"))
        assertEquals("rendered_fields", mapper.toColumnName("renderedFields"))
        assertEquals("my_column", mapper.toColumnName("my-column"))
    }

    @Test
    fun `Default mapper does not lowercase table names even when toggle is enabled`() {
        val mapper =
            S3DataLakeDefaultTableSchemaMapper(tempTableNameGenerator, lowercaseColumnNames = true)
        val descriptor = DestinationStream.Descriptor("MyNamespace", "MyTable")
        val tableName = mapper.toFinalTableName(descriptor)
        assertEquals("MyNamespace", tableName.namespace)
        assertEquals("MyTable", tableName.name)
    }

    @Test
    fun `Default mapper passes table names through unchanged`() {
        val mapper = S3DataLakeDefaultTableSchemaMapper(tempTableNameGenerator)
        val descriptor = DestinationStream.Descriptor("MyNamespace", "MyTable")
        val tableName = mapper.toFinalTableName(descriptor)
        assertEquals("MyNamespace", tableName.namespace)
        assertEquals("MyTable", tableName.name)
    }

    @Test
    fun `Default mapper uses empty namespace when descriptor namespace is null`() {
        val mapper = S3DataLakeDefaultTableSchemaMapper(tempTableNameGenerator)
        val descriptor = DestinationStream.Descriptor(null, "MyTable")
        val tableName = mapper.toFinalTableName(descriptor)
        assertEquals("", tableName.namespace)
        assertEquals("MyTable", tableName.name)
    }

    // -- toSnakeCaseColumnName unit tests --

    @Test
    fun `toSnakeCaseColumnName handles standard camelCase`() {
        assertEquals("project_id", toSnakeCaseColumnName("projectId"))
        assertEquals("first_name", toSnakeCaseColumnName("firstName"))
        assertEquals("versioned_representations", toSnakeCaseColumnName("versionedRepresentations"))
    }

    @Test
    fun `toSnakeCaseColumnName handles already snake_case`() {
        assertEquals("project_id", toSnakeCaseColumnName("project_id"))
        assertEquals("first_name", toSnakeCaseColumnName("first_name"))
    }

    @Test
    fun `toSnakeCaseColumnName handles PascalCase`() {
        assertEquals("project_id", toSnakeCaseColumnName("ProjectId"))
        assertEquals("first_name", toSnakeCaseColumnName("FirstName"))
    }

    @Test
    fun `toSnakeCaseColumnName handles SCREAMING_CASE`() {
        assertEquals("project_id", toSnakeCaseColumnName("PROJECT_ID"))
        assertEquals("field_with_all_caps", toSnakeCaseColumnName("FIELD_WITH_ALL_CAPS"))
    }

    @Test
    fun `toSnakeCaseColumnName handles all-uppercase without separators`() {
        // No word boundaries to detect — stays as one word
        assertEquals("projectid", toSnakeCaseColumnName("PROJECTID"))
        assertEquals("url", toSnakeCaseColumnName("URL"))
    }

    @Test
    fun `toSnakeCaseColumnName handles acronyms followed by words`() {
        assertEquals("html_parser", toSnakeCaseColumnName("HTMLParser"))
        assertEquals("io_stream", toSnakeCaseColumnName("IOStream"))
        assertEquals("get_http_response", toSnakeCaseColumnName("getHTTPResponse"))
        assertEquals("my_url", toSnakeCaseColumnName("myURL"))
    }

    @Test
    fun `toSnakeCaseColumnName handles single word`() {
        assertEquals("id", toSnakeCaseColumnName("id"))
        assertEquals("name", toSnakeCaseColumnName("Name"))
        assertEquals("name", toSnakeCaseColumnName("NAME"))
    }

    @Test
    fun `toSnakeCaseColumnName handles special characters`() {
        assertEquals("foo_bar", toSnakeCaseColumnName("Foo.Bar"))
        assertEquals(
            "field_name_with_operator_1",
            toSnakeCaseColumnName("field_name_with_operator+1"),
        )
    }

    @Test
    fun `toSnakeCaseColumnName handles testFunkyCharacters column names`() {
        // These are the exact column names from the testFunkyCharacters integration test
        assertEquals("field_with_camel_case", toSnakeCaseColumnName("fieldWithCamelCase"))
        assertEquals("proper_case", toSnakeCaseColumnName("ProperCase"))
        assertEquals("field_with_all_caps", toSnakeCaseColumnName("FIELD_WITH_ALL_CAPS"))
        assertEquals("field_with_underscore", toSnakeCaseColumnName("field_with_underscore"))
        assertEquals(
            "field_with_special_character",
            toSnakeCaseColumnName("field_with_spécial_character"),
        )
        assertEquals(
            "field_name_with_operator_1",
            toSnakeCaseColumnName("field_name_with_operator+1"),
        )
        assertEquals(
            "1field_with_a_leading_number",
            toSnakeCaseColumnName("1field_with_a_leading_number"),
        )
        assertEquals("order", toSnakeCaseColumnName("order"))
        assertEquals("foo_bar", toSnakeCaseColumnName("Foo.Bar"))
    }
}
