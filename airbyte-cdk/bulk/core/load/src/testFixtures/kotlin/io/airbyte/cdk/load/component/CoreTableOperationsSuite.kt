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
import kotlin.test.assertNotEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
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
        inputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, AirbyteValue>>,
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

        client.insertRecords(testTable, inputRecords)

        val tableRead = client.readTable((testTable))

        assertEquals(1, tableRead.size) {
            "More than 1 test record was found in ${testTable.namespace}.${testTable.name}"
        }

        val resultRecords = tableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

        assertEquals(expectedRecords, resultRecords)

        client.dropTable(testTable)

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
        }
    }

    fun `insert record`() =
        `insert record`(
            inputRecords = listOf(mapOf("test" to IntegerValue(42))),
            expectedRecords = listOf(mapOf("test" to IntegerValue(42))),
        )

    fun `count table rows`() = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable =
            TableName(
                "default",
                "count-test-table-$uniquePostFix",
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

    fun `overwrite tables`(
        inputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, AirbyteValue>>,
    ) = runTest {
        val uniquePostFix = UUID.randomUUID()
        val sourceTable =
            TableName(
                "default",
                "overwrite-test-source-table-$uniquePostFix",
            )

        assert(!client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} already exists. Please validate it's deleted before running again."
        }

        client.createTable(
            stream =
                DestinationStream(
                    unmappedNamespace = sourceTable.namespace,
                    unmappedName = sourceTable.name,
                    importType = Append,
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    includeFiles = false,
                    schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, false))),
                    namespaceMapper = NamespaceMapper(),
                ),
            tableName = sourceTable,
            columnNameMapping = ColumnNameMapping(mapOf("test" to "test")),
            replace = false,
        )
        assert(client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} was not created as expected."
        }

        client.insertRecords(sourceTable, inputRecords)

        val sourceTableRead = client.readTable((sourceTable))
        val sourceTableRecords = sourceTableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

        assertEquals(expectedRecords, sourceTableRecords) { "Expected records were not loaded into the source table." }

        val targetTable =
            TableName(
                "default",
                "overwrite-test-target-table-$uniquePostFix",
            )

        assert(!client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} already exists. Please validate it's deleted before running again."
        }

        client.createTable(
            stream =
                DestinationStream(
                    unmappedNamespace = targetTable.namespace,
                    unmappedName = targetTable.name,
                    importType = Append,
                    generationId = 1,
                    minimumGenerationId = 0,
                    syncId = 1,
                    includeFiles = false,
                    schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, false))),
                    namespaceMapper = NamespaceMapper(),
                ),
            tableName = targetTable,
            columnNameMapping = ColumnNameMapping(mapOf("test" to "test")),
            replace = false,
        )

        assert(client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} was not created as expected."
        }

        val targetTableInputRecords = listOf(
            mapOf("test" to IntegerValue(124)),
            mapOf("test" to IntegerValue(8724)),
            mapOf("test" to IntegerValue(1337)),
        )

        assertNotEquals(inputRecords, targetTableInputRecords) {
            "Source and target table input records must be different to properly test overwrite."
        }

        client.insertRecords(targetTable, targetTableInputRecords)

        val insertedIntoTargetCount = client.countTable(targetTable)?.toInt()
        val expectedTargetRecordCount = targetTableInputRecords.size
        assertEquals(expectedTargetRecordCount, insertedIntoTargetCount) {
            "Expected count of records were not inserted into target table."
        }

        client.overwriteTable(sourceTable, targetTable)

        val overwrittenTableRead = client.readTable(targetTable)
        val overwrittenTableRecords = overwrittenTableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

        assertEquals(expectedRecords, overwrittenTableRecords)  { "Expected records were not in the overwritten table." }

        client.dropTable(sourceTable)

        assert(!client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} was not dropped as expected."
        }

        client.dropTable(targetTable)

        assert(!client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} was not dropped as expected."
        }
    }

    fun `overwrite tables`() = `overwrite tables`(
        listOf(
            mapOf("test" to IntegerValue(123)),
            mapOf("test" to IntegerValue(456)),
        ),
        listOf(
            mapOf("test" to IntegerValue(123)),
            mapOf("test" to IntegerValue(456)),
        ),
    )

    fun `copy tables`() {}

    fun `upsert tables`() {}

    fun `get generation id`() {}
}
