/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsFixtures.inputRecord
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeAirbyteColumns
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeNulls
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions.assertEquals

private val log = KotlinLogging.logger {}

/**
 * Helper class that encapsulates common test operations for CoreTableOperationsSuite. Provides
 * utility methods for creating, dropping, and verifying tables with proper cleanup.
 */
class TableOperationsTestHarness(
    private val client: TableOperationsClient,
    private val testClient: TestTableOperationsClient,
    private val schemaFactory: TableSchemaFactory,
    private val airbyteMetaColumnMapping: Map<String, String>,
) {

    /** Creates a test table with the given configuration and verifies it was created. */
    suspend fun createTestTableAndVerifyExists(
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        stream: DestinationStream
    ) {
        client.createTable(
            stream = stream,
            tableName = tableName,
            columnNameMapping = columnNameMapping,
            replace = false,
        )
        assert(client.tableExists(tableName)) {
            "test table: ${tableName.namespace}.${tableName.name} was not created as expected."
        }
    }

    /** Safely drops a table, logging any errors. */
    suspend fun cleanupTable(tableName: TableName) {
        try {
            client.dropTable(tableName)
        } catch (e: Exception) {
            log.warn(e) { "Failed cleaning up test resource: $tableName" }
        }
    }

    /** Creates a test namespace and verifies it was created. */
    suspend fun createTestNamespaceVerifyExists(testNamespace: String) {
        assertNamespaceDoesNotExist(testNamespace)

        client.createNamespace(testNamespace)
        assert(client.namespaceExists(testNamespace)) {
            "test namespace: $testNamespace was not created as expected."
        }
    }

    /** Safely drops a namespace, logging any errors. */
    suspend fun cleanupNamespace(namespace: String) {
        try {
            testClient.dropNamespace(namespace)
        } catch (e: Exception) {
            log.warn(e) { "Failed cleaning up test resource: $namespace" }
        }
    }

    /** Ensures a table doesn't exist before test execution. */
    suspend fun assertTableDoesNotExist(tableName: TableName) {
        assert(!client.tableExists(tableName)) {
            "test table: ${tableName.namespace}.${tableName.name} already exists. Please validate it's deleted before running again."
        }
    }

    /** Ensures a namespace doesn't exist before test execution. */
    suspend fun assertNamespaceDoesNotExist(namespace: String) {
        assert(!client.namespaceExists(namespace)) {
            "test namespace: $namespace already exists. Please validate it's deleted before running again."
        }
    }

    /** Inserts records and verifies the count matches expected. */
    suspend fun insertAndVerifyRecordCount(
        tableName: TableName,
        records: List<Map<String, AirbyteValue>>,
        columnNameMapping: ColumnNameMapping,
    ) {
        testClient.insertRecords(tableName, records, columnNameMapping)
        val actualCount = client.countTable(tableName)?.toInt()

        assertEquals(records.size, actualCount) {
            "Expected $records.size records in ${tableName.namespace}.${tableName.name}, but found $actualCount"
        }
    }

    /** Reads records from a table, filtering out Meta columns. */
    suspend fun readTableWithoutMetaColumns(tableName: TableName): List<Map<String, Any>> {
        val tableRead = testClient.readTable(tableName)
        return tableRead.removeAirbyteColumns(airbyteMetaColumnMapping)
    }

    /** Apply the coercer to a value and verify that we can write the coerced value correctly */
    suspend fun testValueCoercion(
        coercer: ValueCoercer,
        columnNameMapping: ColumnNameMapping,
        fieldType: FieldType,
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        val testNamespace = TableOperationsFixtures.generateTestNamespace("test")
        val tableName =
            TableOperationsFixtures.generateTestTableName("table-test-table", testNamespace)
        val schema = ObjectType(linkedMapOf("test" to fieldType))
        val tableSchema = schemaFactory.make(tableName, schema.properties, Append)
        val stream =
            TableOperationsFixtures.createStream(
                namespace = tableName.namespace,
                name = tableName.name,
                tableSchema = tableSchema,
            )

        val inputValueAsEnrichedAirbyteValue =
            EnrichedAirbyteValue(
                inputValue,
                fieldType.type,
                "test",
                airbyteMetaField = null,
            )
        val mappedValue = coercer.map(inputValueAsEnrichedAirbyteValue)
        val validatedValue = coercer.validate(mappedValue)
        val valueToInsert: AirbyteValue
        val changeReason: Reason?
        when (validatedValue) {
            is ValidationResult.ShouldNullify -> {
                valueToInsert = NullValue
                changeReason = validatedValue.reason
            }
            is ValidationResult.ShouldTruncate -> {
                valueToInsert = validatedValue.truncatedValue
                changeReason = validatedValue.reason
            }
            ValidationResult.Valid -> {
                valueToInsert = mappedValue.abValue
                changeReason = null
            }
        }

        client.createNamespace(testNamespace)
        client.createTable(stream, tableName, columnNameMapping, replace = false)
        testClient.insertRecords(
            tableName,
            columnNameMapping,
            inputRecord("test" to valueToInsert),
        )

        val actualRecords =
            testClient
                .readTable(tableName)
                .removeAirbyteColumns(airbyteMetaColumnMapping)
                .reverseColumnNameMapping(columnNameMapping, airbyteMetaColumnMapping)
                .removeNulls()
        val actualValue = actualRecords.first()["test"]
        assertEquals(
            expectedValue,
            actualValue,
            "For input $inputValue, expected ${expectedValue.simpleClassName()}; actual value was ${actualValue.simpleClassName()}. Coercer output was $validatedValue.",
        )
        assertEquals(expectedChangeReason, changeReason)
    }
}

fun Any?.simpleClassName() = this?.let { it::class.simpleName } ?: "null"
