/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table.directload

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.write.StreamStateStore
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

/**
 * Tests that DirectLoadTable stream loaders properly recreate non-empty temp tables on retry to
 * prevent accumulating records from prior failed sync attempts.
 *
 * Bug context: When a sync attempt fails, its partial records remain in the temp table. On retry,
 * the new attempt's records were being appended to the existing partial data instead of starting
 * fresh, causing duplicate rows in the destination.
 */
class DirectLoadTableStreamLoaderTest {

    private val stream =
        mockk<DestinationStream>(relaxed = true) {
            every { mappedDescriptor } returns mockk(relaxed = true)
            every { minimumGenerationId } returns 1L
            every { generationId } returns 1L
        }

    private val realTableName = TableName(namespace = "ns", name = "real_table")
    private val tempTableName = TableName(namespace = "ns", name = "temp_table")
    private val columnNameMapping = ColumnNameMapping(emptyMap())
    private val schemaEvolutionClient = mockk<TableSchemaEvolutionClient>(relaxed = true)
    private val tableOperationsClient = mockk<TableOperationsClient>(relaxed = true)
    private val streamStateStore =
        mockk<StreamStateStore<DirectLoadTableExecutionConfig>>(relaxed = true)
    private val tempTableNameGenerator = mockk<TempTableNameGenerator>(relaxed = true)

    // --- DedupStreamLoader tests ---

    @Test
    fun `DedupStreamLoader should recreate non-empty temp table on retry`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = false),
            )

        val loader =
            DirectLoadTableDedupStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
            )

        loader.start()

        // Should recreate the non-empty temp table, not just ensure schema matches
        coVerify(exactly = 1) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
        coVerify(exactly = 0) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
    }

    @Test
    fun `DedupStreamLoader should reuse empty temp table`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = true),
            )

        val loader =
            DirectLoadTableDedupStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
            )

        loader.start()

        // Should only ensure schema matches for an empty temp table
        coVerify(exactly = 1) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
        coVerify(exactly = 0) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
    }

    // --- AppendTruncateStreamLoader tests ---

    @Test
    fun `AppendTruncateStreamLoader should recreate non-empty temp table on retry`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = false),
            )

        val loader =
            DirectLoadTableAppendTruncateStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
            )

        loader.start()

        // Should recreate the non-empty temp table, not just ensure schema matches
        coVerify(exactly = 1) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
        coVerify(exactly = 0) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
    }

    @Test
    fun `AppendTruncateStreamLoader should reuse empty temp table`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = true),
            )

        val loader =
            DirectLoadTableAppendTruncateStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
            )

        loader.start()

        // Should only ensure schema matches for an empty temp table
        coVerify(exactly = 1) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
        coVerify(exactly = 0) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
    }

    // --- DedupTruncateStreamLoader tests ---

    @Test
    fun `DedupTruncateStreamLoader should recreate non-empty temp table on retry`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = false),
            )

        coEvery { tableOperationsClient.getGenerationId(tempTableName) } returns 1L

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
                tempTableNameGenerator,
            )

        loader.start()

        // Should recreate the non-empty temp table, not just ensure schema matches
        coVerify(exactly = 1) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
        coVerify(exactly = 0) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
    }

    @Test
    fun `DedupTruncateStreamLoader should reuse empty temp table`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = true),
            )

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
                tempTableNameGenerator,
            )

        loader.start()

        // Should only ensure schema matches for an empty temp table
        coVerify(exactly = 1) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
        coVerify(exactly = 0) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
    }

    @Test
    fun `DedupTruncateStreamLoader should create new temp table when none exists`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = null,
            )

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream,
                initialStatus,
                realTableName,
                tempTableName,
                columnNameMapping,
                schemaEvolutionClient,
                tableOperationsClient,
                streamStateStore,
                tempTableNameGenerator,
            )

        loader.start()

        // Should create a fresh temp table
        coVerify(exactly = 1) {
            tableOperationsClient.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true
            )
        }
    }
}
