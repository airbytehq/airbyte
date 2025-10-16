/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.sortByTestField
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.message.Meta
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

    private val harness: TableOperationsTestHarness
        get() = TableOperationsTestHarness(client)

    /** Tests basic database connectivity by pinging the database. */
    fun `connect to database`() = runTest { assertDoesNotThrow { client.ping() } }

    /** Tests namespace creation and deletion operations. */
    fun `create and drop namespaces`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        harness.assertNamespaceDoesNotExist(testNamespace)

        try {
            client.createNamespace(testNamespace)

            assert(client.namespaceExists(testNamespace))

            client.dropNamespace(testNamespace)

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

        try {

            client.createTable(
                tableName = testTable,
                columnNameMapping = Fixtures.TEST_MAPPING,
                stream =
                    Fixtures.createAppendStream(
                        namespace = testTable.namespace,
                        name = testTable.name,
                        schema = Fixtures.TEST_INTEGER_SCHEMA,
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
     */
    fun `insert records`(
        inputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("insert-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("insert-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                schema = Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping = Fixtures.TEST_MAPPING,
            )

            client.insertRecords(testTable, inputRecords)

            val resultRecords = harness.readTableWithoutMetaColumns(testTable)

            assertEquals(expectedRecords, resultRecords)
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
        )

    /** Tests the ability to count rows in a table across multiple insertions. */
    fun `count table rows`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("count-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("count-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                schema = Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping = Fixtures.TEST_MAPPING,
            )

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
        } finally {
            harness.cleanupTable(testTable)
            harness.cleanupNamespace(testNamespace)
        }
    }

    /** Tests retrieval of the generation ID from inserted records. */
    fun `get generation id`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("gen-id-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val testTable = Fixtures.generateTestTableName("gen-id-test-table", testNamespace)
        harness.assertTableDoesNotExist(testTable)

        try {
            harness.createTestTableAndVerifyExists(
                tableName = testTable,
                schema = Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping = Fixtures.TEST_MAPPING,
            )

            val genId = 17L
            val inputRecords =
                listOf(
                    mapOf(
                        Fixtures.TEST_FIELD to IntegerValue(42),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(genId),
                    ),
                )
            client.insertRecords(testTable, inputRecords)

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
     */
    fun `overwrite tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
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

        try {
            harness.createTestTableAndVerifyExists(
                sourceTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                Fixtures.TEST_MAPPING
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords)

            harness.createTestTableAndVerifyExists(
                targetTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                Fixtures.TEST_MAPPING
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords)

            client.overwriteTable(sourceTable, targetTable)

            val overwrittenTableRecords = harness.readTableWithoutMetaColumns(targetTable)

            assertEquals(
                expectedRecords.sortByTestField(),
                overwrittenTableRecords.sortByTestField(),
            ) {
                "Expected records were not in the overwritten table."
            }

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
        )

    /**
     * Tests table copy functionality where records from a source table are copied to a target
     * table.
     *
     * @param sourceInputRecords Records in the source table to be copied
     * @param targetInputRecords Existing records in the target table
     * @param expectedRecords Expected combined records in the target table after copy
     */
    fun `copy tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("overwrite-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val sourceTable = Fixtures.generateTestTableName("copy-test-source-table", testNamespace)
        val targetTable = Fixtures.generateTestTableName("copy-test-target-table", testNamespace)

        harness.assertTableDoesNotExist(sourceTable)
        harness.assertTableDoesNotExist(targetTable)

        try {
            harness.createTestTableAndVerifyExists(
                sourceTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                Fixtures.TEST_MAPPING
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords)

            harness.createTestTableAndVerifyExists(
                targetTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                Fixtures.TEST_MAPPING
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords)

            client.copyTable(Fixtures.TEST_MAPPING, sourceTable, targetTable)

            val copyTableRecords = harness.readTableWithoutMetaColumns(targetTable)

            assertEquals(
                expectedRecords.sortByTestField(),
                copyTableRecords.sortByTestField(),
            ) {
                "Expected source records were not copied to the target table."
            }
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
        )

    /**
     * Tests table upsert functionality with deduplication based on primary key. Records are updated
     * if they exist, inserted if they don't, and deleted if marked with CDC_DELETED_AT.
     *
     * @param sourceInputRecords Records to upsert from the source table
     * @param targetInputRecords Existing records in the target table
     * @param expectedRecords Expected records in the target table after upsert
     */
    fun `upsert tables`(
        sourceInputRecords: List<Map<String, AirbyteValue>>,
        targetInputRecords: List<Map<String, AirbyteValue>>,
        expectedRecords: List<Map<String, Any>>,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("upsert-test-namespace")
        harness.createTestNamespaceVerifyExists(testNamespace)

        val sourceTable = Fixtures.generateTestTableName("upsert-test-source-table", testNamespace)

        harness.assertTableDoesNotExist(sourceTable)

        val sourceStream =
            Fixtures.createAppendStream(
                namespace = sourceTable.namespace,
                name = sourceTable.name,
                schema = Fixtures.ID_AND_TEST_SCHEMA,
            )

        val targetTable = Fixtures.generateTestTableName("upsert-test-target-table", testNamespace)

        harness.assertTableDoesNotExist(targetTable)

        val targetStream =
            Fixtures.createDedupeStream(
                namespace = targetTable.namespace,
                name = targetTable.name,
                schema = Fixtures.ID_TEST_WITH_CDC_SCHEMA,
                primaryKey = listOf(listOf(Fixtures.ID_FIELD)),
                cursor = listOf(Fixtures.TEST_FIELD),
            )

        try {
            harness.createTestTableAndVerifyExists(
                tableName = sourceTable,
                columnNameMapping = Fixtures.ID_TEST_WITH_CDC_MAPPING,
                schema = Fixtures.ID_AND_TEST_SCHEMA,
                stream = sourceStream,
            )
            harness.insertAndVerifyRecordCount(sourceTable, sourceInputRecords)

            harness.createTestTableAndVerifyExists(
                tableName = targetTable,
                columnNameMapping = Fixtures.ID_TEST_WITH_CDC_MAPPING,
                schema = Fixtures.ID_TEST_WITH_CDC_SCHEMA,
                stream = targetStream,
            )
            harness.insertAndVerifyRecordCount(targetTable, targetInputRecords)

            client.upsertTable(
                targetStream,
                Fixtures.ID_TEST_WITH_CDC_MAPPING,
                sourceTable,
                targetTable
            )

            val upsertTableRecords = harness.readTableWithoutMetaColumns(targetTable)

            assertEquals(
                expectedRecords.sortByTestField(),
                upsertTableRecords.sortByTestField(),
            ) {
                "Upserted table did not contain expected records."
            }
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
        )
}
