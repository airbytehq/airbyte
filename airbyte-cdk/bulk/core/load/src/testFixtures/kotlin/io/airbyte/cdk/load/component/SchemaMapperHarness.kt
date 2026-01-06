/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.ColumnNameMapping
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.assertDoesNotThrow

class SchemaMapperHarness(
    val tableSchemaMapper: TableSchemaMapper,
    val schemaFactory: TableSchemaFactory,
    val opsClient: TableOperationsClient,
) {
    fun testTableIdentifiers(namespace: String, name: String, expectedTableName: TableName) =
        runTest {
            val tableName =
                tableSchemaMapper.toFinalTableName(DestinationStream.Descriptor(namespace, name))
            assertEquals(expectedTableName, tableName)
            validateCreateTableWithNameAndSchema(tableName)
        }

    fun testTempTableIdentifiers(namespace: String, name: String, expectedTableName: TableName) =
        runTest {
            val inputTableName = TableName(namespace, name)
            val tempTableName = tableSchemaMapper.toTempTableName(inputTableName)
            assertEquals(expectedTableName, tempTableName)
            validateCreateTableWithNameAndSchema(tempTableName)
        }

    fun testColumnIdentifiers(columnName: String, expectedColumnName: String) = runTest {
        val mappedColumnName = tableSchemaMapper.toColumnName(columnName)
        assertEquals(expectedColumnName, mappedColumnName)
        validateCreateTableWithColumnName(mappedColumnName)
    }

    /**
     * Validate that creating a table works. Uses a default table name, and always maps the column
     * to an integer type.
     */
    suspend fun validateCreateTableWithColumnName(inputColumnName: String) {
        val inputSchema = mapOf(inputColumnName to SchemaMapperSuite.intType)
        val mappedTypes = inputSchema.mapValues { (_, v) -> tableSchemaMapper.toColumnType(v) }
        validateCreateTableWithSchema(
            inputSchema,
            mappedTypes,
        )
    }

    /** Validate that creating a table with the given schema works. Uses a default table name. */
    suspend fun validateCreateTableWithSchema(
        inputSchema: Map<String, FieldType>,
        mappedTypes: Map<String, ColumnType>,
    ) {
        val tableName = tableSchemaMapper.toFinalTableName(columnNameTestStreamDescriptor)
        val inputToFinalColumnNames =
            inputSchema.keys.associateWith { tableSchemaMapper.toColumnName(it) }
        val finalSchema =
            mappedTypes.mapKeys { (fieldName, _) -> tableSchemaMapper.toColumnName(fieldName) }
        validateCreateTableWithNameAndSchema(
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

    suspend fun validateCreateTableWithNameAndSchema(
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
            this.opsClient.createTable(
                stream,
                tableName,
                ColumnNameMapping(emptyMap()),
                replace = true
            )
        }
    }

    companion object {
        val columnNameTestStreamDescriptor =
            DestinationStream.Descriptor("column-names-test-namespace", "column-names-test-table")
    }
}
