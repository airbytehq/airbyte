/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.ID_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.TEST_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.message.Meta
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.assertAll

@MicronautTest(environments = ["component"])
interface TableSchemaEvolutionSuite {
    val client: TableSchemaEvolutionClient
    val airbyteMetaColumnMapping: Map<String, String>
        get() = Meta.COLUMN_NAMES.associateWith { it }

    val opsClient: TableOperationsClient
    val testClient: TestTableOperationsClient

    private val harness: TableOperationsTestHarness
        get() = TableOperationsTestHarness(opsClient, testClient, airbyteMetaColumnMapping)

    fun `noop diff`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val stream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = Fixtures.TEST_INTEGER_SCHEMA,
            )

        opsClient.createNamespace(testNamespace)
        opsClient.createTable(
            tableName = testTable,
            columnNameMapping = Fixtures.TEST_MAPPING,
            stream = stream,
            replace = false,
        )

        val actualColumns = client.discoverSchema(testTable).columns
        val expectedColumns = client.computeSchema(stream, Fixtures.TEST_MAPPING).columns
        val columnChangeset = client.computeChangeset(actualColumns, expectedColumns)

        assertTrue(columnChangeset.isNoop())
    }

    fun `add column`() = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val initialStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = Fixtures.TEST_INTEGER_SCHEMA,
            )
        val modifiedStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = Fixtures.ID_AND_TEST_SCHEMA,
            )

        opsClient.createNamespace(testNamespace)
        // Create a table with just the `test` column
        opsClient.createTable(
            tableName = testTable,
            columnNameMapping = Fixtures.TEST_MAPPING,
            stream = initialStream,
            replace = false,
        )
        // and insert a single record
        testClient.insertRecords(
            testTable,
            listOf(mapOf(TEST_FIELD to IntegerValue(42))),
            Fixtures.TEST_MAPPING
        )

        val actualColumns = client.discoverSchema(testTable).columns
        // Now simulate a situation where we're adding an `id` column
        val expectedColumns =
            client.computeSchema(modifiedStream, Fixtures.ID_AND_TEST_MAPPING).columns
        val columnChangeset = client.computeChangeset(actualColumns, expectedColumns)

        // The changeset should indicate that we're trying to add a column
        assertAll(
            {
                assertEquals(
                    columnChangeset.columnsToAdd.keys,
                    setOf(Fixtures.ID_AND_TEST_MAPPING[ID_FIELD]),
                    "Expected to add exactly one column. Got ${columnChangeset.columnsToAdd}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToDrop.size,
                    "Expected to not drop any columns. Got ${columnChangeset.columnsToDrop}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToChange.size,
                    "Expected to not change any columns. Got ${columnChangeset.columnsToChange}"
                )
            },
            {
                assertEquals(
                    columnChangeset.columnsToRetain.keys,
                    setOf(Fixtures.ID_AND_TEST_MAPPING[TEST_FIELD]),
                    "Expected to retain the original column. Got ${columnChangeset.columnsToRetain}"
                )
            },
        )

        // Apply the changes
        client.applyChangeset(
            modifiedStream,
            Fixtures.TEST_MAPPING,
            testTable,
            expectedColumns,
            columnChangeset
        )
        // Refetch the table's schema + recalculate changeset
        val postAlterChangeset =
            client.computeChangeset(client.discoverSchema(testTable).columns, expectedColumns)

        // We should now match the expected schema
        assertTrue(postAlterChangeset.isNoop())

        // And we should preserve the existing record, but now with the `id` field
        val resultRecords = harness.readTableWithoutMetaColumns(testTable)
        Assertions.assertEquals(
            listOf(mapOf(ID_FIELD to null, TEST_FIELD to 42L)),
            resultRecords.reverseColumnNameMapping(
                Fixtures.ID_AND_TEST_MAPPING,
                airbyteMetaColumnMapping,
            )
        )
    }
}
