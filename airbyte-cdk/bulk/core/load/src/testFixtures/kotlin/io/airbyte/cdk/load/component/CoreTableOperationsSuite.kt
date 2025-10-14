/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.CoreTableOperationsClient
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import java.util.UUID
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.assertDoesNotThrow

interface CoreTableOperationsSuite {
    val client: CoreTableOperationsClient

    fun `connect to database`() = runTest { assertDoesNotThrow { client.ping() } }

    fun `create and drop namespaces`() = runTest {
        val testNamespace = "namespace-test-${UUID.randomUUID()}"

        assert(!client.namespaceExists(testNamespace)) {
            "test namespace: $testNamespace already exists. Please validate it's deleted before running again."
        }

        client.createNamespace(testNamespace)

        assert(client.namespaceExists(testNamespace))

        client.dropNamespace(testNamespace)

        assert(!client.namespaceExists(testNamespace))
    }

    fun `create and drop tables`() = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable =
            TableName(
                "default",
                "table-test-table-$uniquePostFix",
            )

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} already exists. Please validate it's deleted before running again."
        }

        client.createTable(
            stream =
                DestinationStream(
                    unmappedNamespace = testTable.namespace,
                    unmappedName = testTable.name,
                    importType = Append,
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    includeFiles = false,
                    schema = ObjectType(linkedMapOf()),
                    namespaceMapper = NamespaceMapper(),
                ),
            tableName = testTable,
            columnNameMapping = ColumnNameMapping(mapOf()),
            replace = false,
        )

        assert(client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not created as expected."
        }

        client.dropTable(testTable)

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
        }
    }

    fun `insert record`(
        inputRecord: Map<String, AirbyteValue>,
        expectedRecord: Map<String, AirbyteValue>,
    ) = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable =
            TableName(
                "default",
                "insert-test-table-$uniquePostFix",
            )

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} already exists. Please validate it's deleted before running again."
        }

        client.createTable(
            stream =
                DestinationStream(
                    unmappedNamespace = testTable.namespace,
                    unmappedName = testTable.name,
                    importType = Append,
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    includeFiles = false,
                    schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, false))),
                    namespaceMapper = NamespaceMapper(),
                ),
            tableName = testTable,
            columnNameMapping = ColumnNameMapping(mapOf("test" to "test")),
            replace = false,
        )
        assert(client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not created as expected."
        }

        client.insertRecords(testTable, listOf(inputRecord))

        val tableRead = client.readTable((testTable))

        assertEquals(1, tableRead.size) {
            "More than 1 test record was found in ${testTable.namespace}.${testTable.name}"
        }

        val resultRecord = tableRead[0].filter { !Meta.COLUMN_NAMES.contains(it.key) }

        assertEquals(expectedRecord, resultRecord)

        client.dropTable(testTable)

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
        }
    }

    fun `insert record`() =
        `insert record`(
            inputRecord = mapOf("test" to IntegerValue(42)),
            expectedRecord = mapOf("test" to IntegerValue(42)),
        )

    fun `count table rows`() = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable =
            TableName(
                "default",
                "insert-test-table-$uniquePostFix",
            )

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} already exists. Please validate it's deleted before running again."
        }

        client.createTable(
            stream =
                DestinationStream(
                    unmappedNamespace = testTable.namespace,
                    unmappedName = testTable.name,
                    importType = Append,
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    includeFiles = false,
                    schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, false))),
                    namespaceMapper = NamespaceMapper(),
                ),
            tableName = testTable,
            columnNameMapping = ColumnNameMapping(mapOf("test" to "test")),
            replace = false,
        )
        assert(client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not created as expected."
        }

        val records1 =
            listOf(
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
            )

        client.insertRecords(testTable, records1)

        val count1 = client.countTable(testTable)

        assertEquals(records1.size, count1?.toInt())

        val records2 =
            listOf(
                mapOf("test" to IntegerValue(42)),
            )

        client.insertRecords(testTable, records2)

        val count2 = client.countTable(testTable)

        assertEquals(records1.size + records2.size, count2?.toInt())

        val records3 =
            listOf(
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
                mapOf("test" to IntegerValue(42)),
            )

        client.insertRecords(testTable, records3)

        val count3 = client.countTable(testTable)

        assertEquals(records1.size + records2.size + records3.size, count3?.toInt())

        client.dropTable(testTable)

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
        }
    }

    fun `overwrite tables`() {}

    fun `copy tables`() {}

    fun `upsert tables`() {}

    fun `get generation id`() {}
}
