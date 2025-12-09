/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.TEST_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.assertEquals
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.assertDoesNotThrow

/**
 * Test suite interface for validating core table operations across different database
 * implementations.
 *
 * This interface provides a comprehensive set of tests for database operations including:
 * - Namespace creation and deletion
 * - Table creation, deletion, and manipulation
 * - Record insertion and retrieval for testing purposes
 * - Table copying, overwriting, and upserting
 *
 * Implementations should provide a [TableOperationsClient] instance configured for their specific
 * database system. The test methods use a [TableOperationsTestHarness] helper to ensure proper
 * cleanup and verification.
 *
 * @see TableOperationsClient
 * @see TableOperationsTestHarness
 * @see TableOperationsFixtures
 */
@MicronautTest(environments = ["component"])
interface TableOperationsSuite {
    /** The database client instance to test. Must be properly configured and connected. */
    val client: TableOperationsClient
    val testClient: TestTableOperationsClient
    val schemaFactory: TableSchemaFactory

    // since ColumnNameMapping doesn't include the airbyte columns...
    val airbyteMetaColumnMapping: Map<String, String>
        get() = Meta.COLUMN_NAMES.associateWith { it }

    private val harness: TableOperationsTestHarness
        get() = TableOperationsTestHarness(client, testClient, airbyteMetaColumnMapping)

    /** Tests basic database connectivity by pinging the database. */
    fun `connect to database`() = runTest { assertDoesNotThrow { testClient.ping() } }

    /** Tests namespace creation and deletion operations. */
    fun `create and drop namespaces`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        harness.assertNamespaceDoesNotExist(testNamespace)

        try {
            client.createNamespace(testNamespace)

            assert(client.namespaceExists(testNamespace))

            testClient.dropNamespace(testNamespace)

            assert(!client.namespaceExists(testNamespace))
        } finally {
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests table creation and deletion operations. */
    fun `create and drop tables`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("table-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        val tableSchema =
            schemaFactory.make(testTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)

        try {

            client.createTable(
                tableName = testTable,
                columnNameMapping = Fixtures.TEST_MAPPING,
                stream =
                    Fixtures.createAppendStream(
                        namespace = testTable.namespace,
                        name = testTable.name,
                        inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                        tableSchema = tableSchema,
                    ),
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
            harness.cleanupTable(testTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /**
     * Tests record insertion functionality.
     *
     * @param inputRecords Records to insert into the test table
     * @param expectedRecords Expected records after insertion (may differ in type representation)
     * @param columnNameMapping Column name mapping to use for the test table
     */
    fun `insert records`(
        inputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("insert-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("insert-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        val tableSchema =
            schemaFactory.make(testTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = tableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                columnNameMapping = columnNameMapping,
                stream = stream,
            )

            testClient.insertRecords(testTable, inputRecords, columnNameMapping)

            val resultRecords = harness.readTableWithoutMetaColumns(testTable)

            assertEquals(
                expectedRecords,
                resultRecords.reverseColumnNameMapping(columnNameMapping, airbyteMetaColumnMapping),
            )
        } finally {
            harness.cleanupTable(testTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests record insertion with default test data. */
    fun `insert records`() =
        `insert records`(
            inputRecords = Fixtures.SINGLE_TEST_RECORD_INPUT,
            expectedRecords = Fixtures.SINGLE_TEST_RECORD_EXPECTED,
            columnNameMapping = Fixtures.TEST_MAPPING,
        )

    fun `count table rows`() = `count table rows`(columnNameMapping = Fixtures.TEST_MAPPING)

    /**
     * Tests the ability to count rows in a table across multiple insertions.
     *
     * @param columnNameMapping Column name mapping to use for the test table
     */
    fun `count table rows`(
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("count-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("count-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        val tableSchema =
            schemaFactory.make(testTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = tableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                columnNameMapping = columnNameMapping,
                stream = stream,
            )

            val records1 =
                listOf(
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("246f1ff1-eae9-4eeb-b02b-9ffecfc46fc1"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("c9f1272d-df1f-4a3f-95d0-3a704676d743"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("0dafda3b-d465-4f34-baf2-85f1887cbb95"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                )

            testClient.insertRecords(testTable, records1, columnNameMapping)

            val count1 = client.countTable(testTable)

            assertEquals(records1.size, count1?.toInt())

            val records2 =
                listOf(
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("ed1fdd92-06ac-465d-ab87-2f0fe1f09f30"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                )

            testClient.insertRecords(testTable, records2, columnNameMapping)

            val count2 = client.countTable(testTable)

            assertEquals(records1.size + records2.size, count2?.toInt())

            val records3 =
                listOf(
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("609ffd26-c8b4-40bb-8020-5b825fc2e585"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("073a10e8-7a9d-40eb-b268-f0f9110b8ba7"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("9ddb052c-3658-46be-9dd2-d81fdde895ea"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("18425373-bb70-4f53-8cac-59f2eba398e6"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("6081dceb-21ef-46be-bcf4-85b3d719d64es"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("71eb9718-c6a0-4c8b-875e-cf2de7d98f52"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                        "test" to IntegerValue(42),
                    ),
                )

            testClient.insertRecords(testTable, records3, columnNameMapping)

            val count3 = client.countTable(testTable)

            assertEquals(records1.size + records2.size + records3.size, count3?.toInt())
        } finally {
            harness.cleanupTable(testTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    fun `get generation id`() = `get generation id`(columnNameMapping = Fixtures.TEST_MAPPING)

    /**
     * Tests retrieval of the generation ID from inserted records.
     *
     * @param columnNameMapping Column name mapping to use for the test table
     */
    fun `get generation id`(
        columnNameMapping: ColumnNameMapping = Fixtures.TEST_MAPPING,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("gen-id-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("gen-id-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        val tableSchema =
            schemaFactory.make(testTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = tableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                columnNameMapping = columnNameMapping,
                stream = stream,
            )

            val genId = 17L
            val inputRecords =
                listOf(
                    mapOf(
                        COLUMN_NAME_AB_RAW_ID to
                            StringValue("59ed9e9f-3197-4be5-9ef6-7caf9cc7ee04"),
                        COLUMN_NAME_AB_EXTRACTED_AT to
                            TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                        COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                        COLUMN_NAME_AB_GENERATION_ID to IntegerValue(genId),
                        Fixtures.TEST_FIELD to IntegerValue(42),
                    ),
                )
            testClient.insertRecords(testTable, inputRecords, columnNameMapping)

            val result = client.getGenerationId(testTable)

            assertEquals(17, result) { "Actual generation id differed from expected." }
        } finally {
            harness.cleanupTable(testTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /**
     * Tests table overwrite functionality where a source table replaces a target table.
     *
     * @param sourceInputRecords Records to insert into the source table
     * @param targetInputRecords Initial records in the target table (will be overwritten)
     * @param expectedRecords Expected records in the target table after overwrite
     * @param columnNameMapping Column name mapping to use for the test tables
     */
    fun `overwrite tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        assertNotEquals(sourceInputRecords, targetInputRecords) {
            "Source and target table input records must be different to properly test overwrite."
        }

        val testNamespace = Fixtures.generateTestNamespace("overwrite-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val sourceTable =
            Fixtures.generateTestTableName("overwrite-test-source-table", testNamespace)
        val targetTable =
            Fixtures.generateTestTableName("overwrite-test-target-table", testNamespace)

        harness.assertTableDoesNotExist(sourceTable)
        harness.assertTableDoesNotExist(targetTable)

        val sourceTableSchema =
            schemaFactory.make(sourceTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val sourceStream =
            Fixtures.createAppendStream(
                namespace = sourceTable.namespace,
                name = sourceTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = sourceTableSchema,
            )

        val targetTableSchema =
            schemaFactory.make(targetTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val targetStream =
            Fixtures.createAppendStream(
                namespace = targetTable.namespace,
                name = targetTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = targetTableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = sourceTable,
                columnNameMapping = columnNameMapping,
                stream = sourceStream,
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords, columnNameMapping)

            harness.createTestTableAndVerifyExists(
                tableName = targetTable,
                columnNameMapping = columnNameMapping,
                stream = targetStream,
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords, columnNameMapping)

            client.overwriteTable(sourceTable, targetTable)

            val overwrittenTableRecords = harness.readTableWithoutMetaColumns(targetTable)

            assertEquals(
                expectedRecords,
                overwrittenTableRecords.reverseColumnNameMapping(
                    columnNameMapping,
                    airbyteMetaColumnMapping,
                ),
                "test",
                "Expected records were not in the overwritten table.",
            )

            assert(!client.tableExists(sourceTable)) {
                "Source table: ${sourceTable.namespace}.${sourceTable.name} was not dropped as expected."
            }
        } finally {
            harness.cleanupTable(sourceTable)
            harness.cleanupTable(targetTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests table overwrite with default test data. */
    fun `overwrite tables`() =
        `overwrite tables`(
            sourceInputRecords = Fixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = Fixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = Fixtures.OVERWRITE_EXPECTED_RECORDS,
            columnNameMapping = Fixtures.TEST_MAPPING,
        )

    /**
     * Tests table copy functionality where records from a source table are copied to a target
     * table.
     *
     * @param sourceInputRecords Records in the source table to be copied
     * @param targetInputRecords Existing records in the target table
     * @param expectedRecords Expected combined records in the target table after copy
     * @param columnNameMapping Column name mapping to use for the test tables
     */
    fun `copy tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("overwrite-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val sourceTable = Fixtures.generateTestTableName("copy-test-source-table", testNamespace)
        val targetTable = Fixtures.generateTestTableName("copy-test-target-table", testNamespace)

        harness.assertTableDoesNotExist(sourceTable)
        harness.assertTableDoesNotExist(targetTable)

        val sourceTableSchema =
            schemaFactory.make(sourceTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val sourceStream =
            Fixtures.createAppendStream(
                namespace = sourceTable.namespace,
                name = sourceTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = sourceTableSchema,
            )

        val targetTableSchema =
            schemaFactory.make(targetTable, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val targetStream =
            Fixtures.createAppendStream(
                namespace = targetTable.namespace,
                name = targetTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                tableSchema = targetTableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = sourceTable,
                columnNameMapping = columnNameMapping,
                stream = sourceStream,
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords, columnNameMapping)

            harness.createTestTableAndVerifyExists(
                tableName = targetTable,
                columnNameMapping = columnNameMapping,
                stream = targetStream,
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords, columnNameMapping)

            client.copyTable(columnNameMapping, sourceTable, targetTable)

            val copyTableRecords = harness.readTableWithoutMetaColumns(targetTable)

            assertEquals(
                expectedRecords,
                copyTableRecords.reverseColumnNameMapping(
                    columnNameMapping,
                    airbyteMetaColumnMapping,
                ),
                "test",
                "Expected source records were not copied to the target table.",
            )
        } finally {
            harness.cleanupTable(sourceTable)
            harness.cleanupTable(targetTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests table copy with default test data. */
    fun `copy tables`() =
        `copy tables`(
            sourceInputRecords = Fixtures.OVERWRITE_SOURCE_RECORDS,
            targetInputRecords = Fixtures.OVERWRITE_TARGET_RECORDS,
            expectedRecords = Fixtures.COPY_EXPECTED_RECORDS,
            columnNameMapping = Fixtures.TEST_MAPPING,
        )

    /**
     * Tests table upsert functionality with deduplication based on primary key. Records are updated
     * if they exist, inserted if they don't, and deleted if marked with CDC_DELETED_AT.
     *
     * @param sourceInputRecords Records to upsert from the source table
     * @param targetInputRecords Existing records in the target table
     * @param expectedRecords Expected records in the target table after upsert
     * @param columnNameMapping Column name mapping to use for the test tables
     */
    fun `upsert tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("upsert-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val sourceTable = Fixtures.generateTestTableName("upsert-test-source-table", testNamespace)

        harness.assertTableDoesNotExist(sourceTable)

        val sourceTableSchema =
            schemaFactory.make(sourceTable, Fixtures.ID_TEST_WITH_CDC_SCHEMA.properties, Append)
        val sourceStream =
            Fixtures.createAppendStream(
                namespace = sourceTable.namespace,
                name = sourceTable.name,
                inputSchema = Fixtures.ID_TEST_WITH_CDC_SCHEMA,
                tableSchema = sourceTableSchema,
            )

        val targetTable = Fixtures.generateTestTableName("upsert-test-target-table", testNamespace)
        harness.assertTableDoesNotExist(targetTable)

        val primaryKey = listOf(listOf(Fixtures.ID_FIELD))
        val cursor = listOf(Fixtures.TEST_FIELD)

        val targetTableSchema =
            schemaFactory.make(
                targetTable,
                Fixtures.TEST_INTEGER_SCHEMA.properties,
                Dedupe(primaryKey, cursor),
            )
        val targetStream =
            Fixtures.createDedupeStream(
                namespace = targetTable.namespace,
                name = targetTable.name,
                inputSchema = Fixtures.TEST_INTEGER_SCHEMA,
                primaryKey = primaryKey,
                cursor = cursor,
                tableSchema = targetTableSchema,
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = sourceTable,
                columnNameMapping = columnNameMapping,
                stream = sourceStream,
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords, columnNameMapping)

            harness.createTestTableAndVerifyExists(
                tableName = targetTable,
                columnNameMapping = columnNameMapping,
                stream = targetStream,
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords, columnNameMapping)

            client.upsertTable(targetStream, columnNameMapping, sourceTable, targetTable)

            val upsertTableRecords = testClient.readTable(targetTable)

            assertEquals(
                expectedRecords,
                upsertTableRecords.reverseColumnNameMapping(
                    columnNameMapping,
                    airbyteMetaColumnMapping,
                ),
                "id",
                "Upserted table did not contain expected records.",
            )
        } finally {
            harness.cleanupTable(sourceTable)
            harness.cleanupTable(targetTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests table upsert with default test data including CDC delete markers. */
    fun `upsert tables`() =
        `upsert tables`(
            sourceInputRecords = Fixtures.UPSERT_SOURCE_RECORDS,
            targetInputRecords = Fixtures.UPSERT_TARGET_RECORDS,
            expectedRecords = Fixtures.UPSERT_EXPECTED_RECORDS,
            columnNameMapping = Fixtures.ID_TEST_WITH_CDC_MAPPING,
        )
}
