/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals

@MicronautTest(environments = ["component"])
interface SchemaMapperSuite {
    val tableSchemaMapper: TableSchemaMapper

    val reservedKeyword: String
        get() = "table"

    fun `simple table name`(expectedTableName: TableName) {
        val namespace = TableOperationsFixtures.generateTestNamespace("namespace-test")
        val name = TableOperationsFixtures.generateTestNamespace("table-test")
        val tableName =
            tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor(namespace, name))
        assertEquals(expectedTableName, tableName)
    }

    fun `funky chars in table name`(expectedTableName: TableName) {
        val namespace =
            TableOperationsFixtures.generateTestNamespace(
                "namespace-test- -`~!@#$%^&*()-=_+[]\\{}|o'O\",./<>?"
            )
        val name =
            TableOperationsFixtures.generateTestNamespace(
                "table-test- -`~!@#$%^&*()-=_+[]\\{}|o'O\",./<>?"
            )
        val tableName =
            tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor(namespace, name))
        assertEquals(expectedTableName, tableName)
    }

    fun `table name starts with non-letter character`(expectedTableName: TableName) {
        val namespace = TableOperationsFixtures.generateTestNamespace("1foo")
        val name = TableOperationsFixtures.generateTestNamespace("1foo")
        val tableName =
            tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor(namespace, name))
        assertEquals(expectedTableName, tableName)
    }

    fun `table name is reserved keyword`(expectedTableName: TableName) {
        val namespace = TableOperationsFixtures.generateTestNamespace(reservedKeyword)
        val name = TableOperationsFixtures.generateTestNamespace(reservedKeyword)
        val tableName =
            tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor(namespace, name))
        assertEquals(expectedTableName, tableName)
    }

    // Intentionally no complex coverage here. We're passing in a pre-munged tablename (i.e should
    // already have special chars, etc. handled).
    fun `simple temp table name`(expectedTableName: TableName) {
        val inputTableName = TableName("foo", "bar")
        val tempTableName = tableSchemaMapper.toTempTableName(inputTableName)
        assertEquals(expectedTableName, tempTableName)
    }

    fun `simple column name`(expectedColumnName: String) {
        val columnName = tableSchemaMapper.toColumnName("column-test")
        assertEquals(expectedColumnName, columnName)
    }

    fun `column name with funky chars`(expectedColumnName: String) {
        val columnName =
            tableSchemaMapper.toColumnName("column-test- -`~!@#$%^&*()-=_+[]\\{}|o'O\",./<>?")
        assertEquals(expectedColumnName, columnName)
    }

    fun `column name starts with non-letter character`(expectedColumnName: String) {
        val columnName = tableSchemaMapper.toColumnName("1foo")
        assertEquals(expectedColumnName, columnName)
    }

    fun `column name is reserved keyword`(expectedColumnName: String) {
        val columnName = tableSchemaMapper.toColumnName(reservedKeyword)
        assertEquals(expectedColumnName, columnName)
    }

    fun `column types support all airbyte types`(expectedTypes: Map<String, ColumnType>) {
        val mappedTypes =
            TableOperationsFixtures.ALL_TYPES_SCHEMA.properties.mapValues { (_, v) ->
                tableSchemaMapper.toColumnType(v)
            }
        assertEquals(expectedTypes, mappedTypes)
    }
}
