/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.SchemaMapperSuite.Companion.columnNameTestStreamDescriptor
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.assertDoesNotThrow

@MicronautTest(environments = ["component"])
interface SchemaMapperSuite {
    val tableSchemaMapper: TableSchemaMapper
    val schemaFactory: TableSchemaFactory
    val opsClient: TableOperationsClient

    val reservedKeyword: String
        get() = "table"

    fun `simple table name`(expectedTableName: TableName) = runTest {
        val tableName =
            tableSchemaMapper.toFinalTableName(
                DestinationStream.Descriptor("namespace-test", "table-test")
            )
        assertEquals(expectedTableName, tableName)
        validateCreateTable(tableName)
    }

    fun `funky chars in table name`(expectedTableName: TableName) = runTest {
        val tableName =
            tableSchemaMapper.toFinalTableName(
                DestinationStream.Descriptor(
                    """namespace-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?""",
                    """table-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?"""
                )
            )
        assertEquals(expectedTableName, tableName)
        validateCreateTable(tableName)
    }

    fun `table name starts with non-letter character`(expectedTableName: TableName) = runTest {
        val tableName =
            tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor("1foo", "1foo"))
        assertEquals(expectedTableName, tableName)
        validateCreateTable(tableName)
    }

    fun `table name is reserved keyword`(expectedTableName: TableName) = runTest {
        val tableName =
            tableSchemaMapper.toFinalTableName(
                DestinationStream.Descriptor(reservedKeyword, reservedKeyword)
            )
        assertEquals(expectedTableName, tableName)
        validateCreateTable(tableName)
    }

    // Intentionally no complex coverage here. We're passing in a pre-munged tablename (i.e should
    // already have special chars, etc. handled).
    fun `simple temp table name`(expectedTableName: TableName) = runTest {
        val inputTableName = TableName("foo", "bar")
        val tempTableName = tableSchemaMapper.toTempTableName(inputTableName)
        assertEquals(expectedTableName, tempTableName)
        validateCreateTable(tempTableName)
    }

    fun `simple column name`(expectedColumnName: String) = runTest {
        val columnName = tableSchemaMapper.toColumnName("column-test")
        assertEquals(expectedColumnName, columnName)
        validateCreateTable(columnName)
    }

    fun `column name with funky chars`(expectedColumnName: String) = runTest {
        val columnName =
            tableSchemaMapper.toColumnName("""column-test- -`~!@#$%^&*()-=_+[]\{}|;':",./<>?""")
        assertEquals(expectedColumnName, columnName)
        validateCreateTable(columnName)
    }

    fun `column name starts with non-letter character`(expectedColumnName: String) = runTest {
        val columnName = tableSchemaMapper.toColumnName("1foo")
        assertEquals(expectedColumnName, columnName)
        validateCreateTable(columnName)
    }

    fun `column name is reserved keyword`(expectedColumnName: String) = runTest {
        val columnName = tableSchemaMapper.toColumnName(reservedKeyword)
        assertEquals(expectedColumnName, columnName)
        validateCreateTable(columnName)
    }

    fun `column types support all airbyte types`(expectedTypes: Map<String, ColumnType>) = runTest {
        val mappedTypes =
            TableOperationsFixtures.ALL_TYPES_SCHEMA.properties.mapValues { (_, v) ->
                tableSchemaMapper.toColumnType(v)
            }
        assertEquals(expectedTypes, mappedTypes)
        validateCreateTable(
            TableOperationsFixtures.ALL_TYPES_SCHEMA.properties,
            mappedTypes,
        )
    }

    companion object {
        val columnNameTestStreamDescriptor =
            DestinationStream.Descriptor("column-names-test-namespace", "column-names-test-table")
        val intType = FieldType(IntegerType, nullable = true)
    }
}

/**
 * Validate that creating a table works. Uses a default table name, and always maps the column to an
 * integer type.
 */
suspend fun SchemaMapperSuite.validateCreateTable(inputColumnName: String) {
    val inputSchema = mapOf(inputColumnName to SchemaMapperSuite.intType)
    val mappedTypes = inputSchema.mapValues { (_, v) -> tableSchemaMapper.toColumnType(v) }
    validateCreateTable(
        inputSchema,
        mappedTypes,
    )
}

/** Validate that creating a table with the given schema works. Uses a default table name. */
suspend fun SchemaMapperSuite.validateCreateTable(
    inputSchema: Map<String, FieldType>,
    mappedTypes: Map<String, ColumnType>,
) {
    val tableName = tableSchemaMapper.toFinalTableName(columnNameTestStreamDescriptor)
    val inputToFinalColumnNames =
        inputSchema.keys.associateWith { tableSchemaMapper.toColumnName(it) }
    val finalSchema =
        mappedTypes.mapKeys { (fieldName, _) -> tableSchemaMapper.toColumnName(fieldName) }
    validateCreateTable(
        tableName,
        StreamTableSchema(
            TableNames(
                rawTableName = null,
                tempTableName = tableSchemaMapper.toTempTableName(tableName),
                finalTableName = tableName,
            ),
            ColumnSchema(inputSchema, inputToFinalColumnNames, finalSchema),
            Append,
        ),
    )
}

suspend fun SchemaMapperSuite.validateCreateTable(
    tableName: TableName,
    tableSchema: StreamTableSchema = this.schemaFactory.make(tableName, emptyMap(), Append),
) {
    val stream =
        TableOperationsFixtures.createStream(
            namespace = tableName.namespace,
            name = tableName.name,
            tableSchema = tableSchema,
        )
    // We have to set replace=true, otherwise tests will fail b/c we're not randomizing names
    // and therefore the table probably already exists
    assertDoesNotThrow {
        this.opsClient.createNamespace(tableName.namespace)
        this.opsClient.createTable(stream, tableName, ColumnNameMapping(emptyMap()), replace = true)
    }
}
