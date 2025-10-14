/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.CoreTableOperationsClient
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.UUID
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.assertDoesNotThrow

private val log = KotlinLogging.logger {}

interface CoreTableOperationsSuite {
    val client: CoreTableOperationsClient

    fun `connect to database`() = runTest { assertDoesNotThrow { client.ping() } }

    fun `create and drop namespaces`() = runTest {
        val testNamespace = "namespace-test-${UUID.randomUUID()}"

        assert(!client.namespaceExists(testNamespace)) {
            "test namespace: $testNamespace already exists. Please validate it's deleted before running again."
        }

        try {
            client.createNamespace(testNamespace)

            assert(client.namespaceExists(testNamespace))

            client.dropNamespace(testNamespace)

            assert(!client.namespaceExists(testNamespace))
        } finally {
            try {
                client.dropNamespace(testNamespace)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $testNamespace" }
            }
        }
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

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = testTable.namespace,
                        unmappedName = testTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
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
        } finally {
            try {
                client.dropTable(testTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $testTable" }
            }
        }
    }

    fun `insert records`(
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

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = testTable.namespace,
                        unmappedName = testTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
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

            val resultRecords =
                tableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

            assertEquals(expectedRecords, resultRecords)

            client.dropTable(testTable)

            assert(!client.tableExists(testTable)) {
                "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
            }
        } finally {
            try {
                client.dropTable(testTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $testTable" }
            }
        }
    }

    fun `insert records`() =
        `insert records`(
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

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = testTable.namespace,
                        unmappedName = testTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
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
        } finally {
            try {
                client.dropTable(testTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $testTable" }
            }
        }
    }

    fun `overwrite tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, AirbyteValue>>,
    ) = runTest {
        assertNotEquals(sourceInputRecords, targetInputRecords) {
            "Source and target table input records must be different to properly test overwrite."
        }

        val uniquePostFix = UUID.randomUUID()
        val sourceTable =
            TableName(
                "default",
                "overwrite-test-source-table-$uniquePostFix",
            )

        assert(!client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} already exists. Please validate it's deleted before running again."
        }

        val targetTable =
            TableName(
                "default",
                "overwrite-test-target-table-$uniquePostFix",
            )

        assert(!client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} already exists. Please validate it's deleted before running again."
        }

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = sourceTable.namespace,
                        unmappedName = sourceTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
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

            client.insertRecords(sourceTable, sourceInputRecords)

            val insertedIntoSourceCount = client.countTable(sourceTable)?.toInt()
            val expectedSourceRecordCount = sourceInputRecords.size
            assertEquals(expectedSourceRecordCount, insertedIntoSourceCount) {
                "Expected records were not loaded into the source table."
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

            client.insertRecords(targetTable, targetInputRecords)

            val insertedIntoTargetCount = client.countTable(targetTable)?.toInt()
            val expectedTargetRecordCount = targetInputRecords.size
            assertEquals(expectedTargetRecordCount, insertedIntoTargetCount) {
                "Expected records were not loaded into the target table."
            }

            client.overwriteTable(sourceTable, targetTable)

            val overwrittenTableRead = client.readTable(targetTable)
            val overwrittenTableRecords =
                overwrittenTableRead.map { rec ->
                    rec.filter { !Meta.COLUMN_NAMES.contains(it.key) }
                }

            assertEquals(expectedRecords, overwrittenTableRecords) {
                "Expected records were not in the overwritten table."
            }

            assert(!client.tableExists(sourceTable)) {
                "Source table: ${sourceTable.namespace}.${sourceTable.name} was not dropped as expected."
            }

            client.dropTable(targetTable)

            assert(!client.tableExists(targetTable)) {
                "test table: ${targetTable.namespace}.${targetTable.name} was not dropped as expected."
            }
        } finally {
            try {
                client.dropTable(sourceTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $sourceTable" }
            }
            try {
                client.dropTable(targetTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $targetTable" }
            }
        }
    }

    fun `overwrite tables`() =
        `overwrite tables`(
            sourceInputRecords =
                listOf(
                    mapOf("test" to IntegerValue(123)),
                    mapOf("test" to IntegerValue(456)),
                ),
            targetInputRecords =
                listOf(
                    mapOf("test" to IntegerValue(86)),
                    mapOf("test" to IntegerValue(75)),
                    mapOf("test" to IntegerValue(309)),
                ),
            expectedRecords =
                listOf(
                    mapOf("test" to IntegerValue(123)),
                    mapOf("test" to IntegerValue(456)),
                ),
        )

    fun `copy tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, AirbyteValue>>,
    ) = runTest {
        val columnNameMapping = ColumnNameMapping(mapOf("test" to "test"))
        val schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, false)))

        val uniquePostFix = UUID.randomUUID()
        val sourceTable =
            TableName(
                "default",
                "copy-test-source-table-$uniquePostFix",
            )

        assert(!client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} already exists. Please validate it's deleted before running again."
        }

        val targetTable =
            TableName(
                "default",
                "copy-test-target-table-$uniquePostFix",
            )

        assert(!client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} already exists. Please validate it's deleted before running again."
        }

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = sourceTable.namespace,
                        unmappedName = sourceTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
                        schema = schema,
                        namespaceMapper = NamespaceMapper(),
                    ),
                tableName = sourceTable,
                columnNameMapping = columnNameMapping,
                replace = false,
            )
            assert(client.tableExists(sourceTable)) {
                "test table: ${sourceTable.namespace}.${sourceTable.name} was not created as expected."
            }

            client.insertRecords(sourceTable, sourceInputRecords)

            val insertedIntoSourceCount = client.countTable(sourceTable)?.toInt()
            val expectedSourceRecordCount = sourceInputRecords.size
            assertEquals(expectedSourceRecordCount, insertedIntoSourceCount) {
                "Expected records were not loaded into the source table."
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
                        schema = schema,
                        namespaceMapper = NamespaceMapper(),
                    ),
                tableName = targetTable,
                columnNameMapping = columnNameMapping,
                replace = false,
            )

            assert(client.tableExists(targetTable)) {
                "test table: ${targetTable.namespace}.${targetTable.name} was not created as expected."
            }

            client.insertRecords(targetTable, targetInputRecords)

            val insertedIntoTargetCount = client.countTable(targetTable)?.toInt()
            val expectedTargetRecordCount = targetInputRecords.size
            assertEquals(expectedTargetRecordCount, insertedIntoTargetCount) {
                "Expected records were not loaded into the target table."
            }

            client.copyTable(columnNameMapping, sourceTable, targetTable)

            val copyTableRead = client.readTable(targetTable)
            val copyTableRecords =
                copyTableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

            assertEquals(expectedRecords.toSet(), copyTableRecords.toSet()) {
                "Expected source records were not copied to the target table."
            }

            client.dropTable(sourceTable)

            assert(!client.tableExists(sourceTable)) {
                "test table: ${sourceTable.namespace}.${sourceTable.name} was not dropped as expected."
            }

            client.dropTable(targetTable)

            assert(!client.tableExists(targetTable)) {
                "test table: ${targetTable.namespace}.${targetTable.name} was not dropped as expected."
            }
        } finally {
            try {
                client.dropTable(sourceTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $sourceTable" }
            }
            try {
                client.dropTable(targetTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $targetTable" }
            }
        }
    }

    fun `copy tables`() =
        `copy tables`(
            sourceInputRecords =
                listOf(
                    mapOf("test" to IntegerValue(123)),
                    mapOf("test" to IntegerValue(456)),
                ),
            targetInputRecords =
                listOf(
                    mapOf("test" to IntegerValue(86)),
                    mapOf("test" to IntegerValue(75)),
                    mapOf("test" to IntegerValue(309)),
                ),
            expectedRecords =
                listOf(
                    mapOf("test" to IntegerValue(123)),
                    mapOf("test" to IntegerValue(456)),
                    mapOf("test" to IntegerValue(86)),
                    mapOf("test" to IntegerValue(75)),
                    mapOf("test" to IntegerValue(309)),
                ),
        )

    fun `upsert tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, AirbyteValue>>,
    ) = runTest {
        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "id" to "id",
                    "test" to "test",
                    CDC_DELETED_AT_COLUMN to CDC_DELETED_AT_COLUMN,
                ),
            )
        val sourceSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(StringType, false),
                    "test" to FieldType(IntegerType, false),
                ),
            )

        val uniquePostFix = UUID.randomUUID()
        val sourceTable =
            TableName(
                "default",
                "upsert-test-source-table-$uniquePostFix",
            )

        assert(!client.tableExists(sourceTable)) {
            "test table: ${sourceTable.namespace}.${sourceTable.name} already exists. Please validate it's deleted before running again."
        }

        val sourceStream =
            DestinationStream(
                unmappedNamespace = sourceTable.namespace,
                unmappedName = sourceTable.name,
                importType = Append,
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                schema = sourceSchema,
                namespaceMapper = NamespaceMapper(),
            )
        val targetSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(StringType, false),
                    "test" to FieldType(IntegerType, false),
                    CDC_DELETED_AT_COLUMN to FieldType(IntegerType, false),
                ),
            )
        val targetTable =
            TableName(
                "default",
                "upsert-test-target-table-$uniquePostFix",
            )

        assert(!client.tableExists(targetTable)) {
            "test table: ${targetTable.namespace}.${targetTable.name} already exists. Please validate it's deleted before running again."
        }

        val targetStream =
            DestinationStream(
                unmappedNamespace = targetTable.namespace,
                unmappedName = targetTable.name,
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("id")),
                        cursor = listOf("test"),
                    ),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                schema = targetSchema,
                namespaceMapper = NamespaceMapper(),
            )

        try {

            client.createTable(
                stream = sourceStream,
                tableName = sourceTable,
                columnNameMapping = columnNameMapping,
                replace = false,
            )
            assert(client.tableExists(sourceTable)) {
                "test table: ${sourceTable.namespace}.${sourceTable.name} was not created as expected."
            }

            client.insertRecords(sourceTable, sourceInputRecords)

            val insertedIntoSourceCount = client.countTable(sourceTable)?.toInt()
            val expectedSourceRecordCount = sourceInputRecords.size
            assertEquals(expectedSourceRecordCount, insertedIntoSourceCount) {
                "Expected records were not loaded into the source table."
            }

            client.createTable(
                stream = targetStream,
                tableName = targetTable,
                columnNameMapping = columnNameMapping,
                replace = false,
            )

            assert(client.tableExists(targetTable)) {
                "test table: ${targetTable.namespace}.${targetTable.name} was not created as expected."
            }

            client.insertRecords(targetTable, targetInputRecords)

            val insertedIntoTargetCount = client.countTable(targetTable)?.toInt()
            val expectedTargetRecordCount = targetInputRecords.size
            assertEquals(expectedTargetRecordCount, insertedIntoTargetCount) {
                "Expected records were not loaded into the target table."
            }

            client.upsertTable(targetStream, columnNameMapping, sourceTable, targetTable)

            val upsertTableRead = client.readTable(targetTable)
            val upsertTableRecords =
                upsertTableRead.map { rec -> rec.filter { !Meta.COLUMN_NAMES.contains(it.key) } }

            assertEquals(expectedRecords.toSet(), upsertTableRecords.toSet()) {
                "Upserted table did not contain expected records."
            }

            client.dropTable(sourceTable)

            assert(!client.tableExists(sourceTable)) {
                "test table: ${sourceTable.namespace}.${sourceTable.name} was not dropped as expected."
            }

            client.dropTable(targetTable)

            assert(!client.tableExists(targetTable)) {
                "test table: ${targetTable.namespace}.${targetTable.name} was not dropped as expected."
            }
        } finally {
            try {
                client.dropTable(sourceTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $sourceTable" }
            }
            try {
                client.dropTable(targetTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $targetTable" }
            }
        }
    }

    fun `upsert tables`() =
        `upsert tables`(
            sourceInputRecords =
                listOf(
                    mapOf("id" to StringValue("2"), "test" to IntegerValue(86)),
                    mapOf(
                        "id" to StringValue("3"),
                        "test" to IntegerValue(75),
                        CDC_DELETED_AT_COLUMN to IntegerValue(1234),
                    ),
                    mapOf("id" to StringValue("4"), "test" to IntegerValue(309)),
                    mapOf("id" to StringValue("5"), "test" to IntegerValue(309)),
                    mapOf(
                        "id" to StringValue("5"),
                        "test" to IntegerValue(309),
                        CDC_DELETED_AT_COLUMN to IntegerValue(1234),
                    ),
                ),
            targetInputRecords =
                listOf(
                    mapOf("id" to StringValue("1"), "test" to IntegerValue(123)),
                    mapOf("id" to StringValue("2"), "test" to IntegerValue(456)),
                    mapOf("id" to StringValue("3"), "test" to IntegerValue(789)),
                    mapOf("id" to StringValue("4"), "test" to IntegerValue(101112)),
                ),
            expectedRecords =
                listOf(
                    mapOf("id" to StringValue("1"), "test" to IntegerValue(123)),
                    mapOf("id" to StringValue("2"), "test" to IntegerValue(86)),
                    mapOf("id" to StringValue("4"), "test" to IntegerValue(309)),
                ),
        )

    fun `get generation id`() = runTest {
        val uniquePostFix = UUID.randomUUID()
        val testTable =
            TableName(
                "default",
                "gen-id-test-table-$uniquePostFix",
            )

        assert(!client.tableExists(testTable)) {
            "test table: ${testTable.namespace}.${testTable.name} already exists. Please validate it's deleted before running again."
        }

        try {
            client.createTable(
                stream =
                    DestinationStream(
                        unmappedNamespace = testTable.namespace,
                        unmappedName = testTable.name,
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 1,
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

            val genId = 17L
            val inputRecords =
                listOf(
                    mapOf(
                        "test" to IntegerValue(42),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(genId),
                    ),
                )
            client.insertRecords(testTable, inputRecords)

            val result = client.getGenerationId(testTable)

            assertEquals(17, result) { "Actual generation id differed from expected." }

            client.dropTable(testTable)

            assert(!client.tableExists(testTable)) {
                "test table: ${testTable.namespace}.${testTable.name} was not dropped as expected."
            }
        } finally {
            try {
                client.dropTable(testTable)
            } catch (e: Exception) {
                log.warn(e) { "Failed cleaning up test resource: $testTable" }
            }
        }
    }
}
