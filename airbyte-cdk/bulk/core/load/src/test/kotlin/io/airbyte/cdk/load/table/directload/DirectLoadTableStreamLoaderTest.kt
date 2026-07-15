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

class DirectLoadTableStreamLoaderTest {

    private val stream =
        mockk<DestinationStream>(relaxed = true) {
            every { mappedDescriptor } returns
                DestinationStream.Descriptor("test_namespace", "test_stream")
            every { generationId } returns 1L
            every { minimumGenerationId } returns 1L
        }
    private val realTableName = TableName("real_namespace", "real_table")
    private val tempTableName = TableName("temp_namespace", "temp_table")
    private val tempTempTableName = TableName("temp_namespace", "temp_temp_table")
    private val columnNameMapping = ColumnNameMapping(emptyMap())
    private val schemaEvolutionClient = mockk<TableSchemaEvolutionClient>(relaxed = true)
    private val tableOperationsClient = mockk<TableOperationsClient>(relaxed = true)
    private val streamStateStore = StreamStateStore<DirectLoadTableExecutionConfig>()
    private val tempTableNameGenerator =
        mockk<TempTableNameGenerator> {
            every { generate(tempTableName) } returns tempTempTableName
        }

    @Test
    fun `AppendTruncateStreamLoader overwrites a table from a higher generation`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = null,
            )
        coEvery { tableOperationsClient.getGenerationId(realTableName) } returns 2L

        val loader =
            DirectLoadTableAppendTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
            )

        loader.start()
        loader.teardown(completedSuccessfully = true)

        coVerify(exactly = 1) {
            tableOperationsClient.createTempTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true,
            )
        }
        coVerify(exactly = 1) {
            tableOperationsClient.overwriteTable(
                sourceTableName = tempTableName,
                targetTableName = realTableName,
            )
        }
    }

    @Test
    fun `AppendTruncateStreamLoader writes directly to a table from the current generation`() =
        runTest {
            val initialStatus =
                DirectLoadInitialStatus(
                    realTable = DirectLoadTableStatus(isEmpty = false),
                    tempTable = null,
                )
            coEvery { tableOperationsClient.getGenerationId(realTableName) } returns 1L

            val loader =
                DirectLoadTableAppendTruncateStreamLoader(
                    stream = stream,
                    initialStatus = initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping = columnNameMapping,
                    schemaEvolutionClient = schemaEvolutionClient,
                    tableOperationsClient = tableOperationsClient,
                    streamStateStore = streamStateStore,
                )

            loader.start()
            loader.teardown(completedSuccessfully = true)

            coVerify(exactly = 1) {
                schemaEvolutionClient.ensureSchemaMatches(
                    stream,
                    realTableName,
                    columnNameMapping,
                )
            }
            coVerify(exactly = 0) {
                tableOperationsClient.createTempTable(any(), any(), any(), any())
            }
            coVerify(exactly = 0) { tableOperationsClient.overwriteTable(any(), any()) }
        }

    @Test
    fun `AppendTruncateStreamLoader recreates a temp table from a higher generation`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = false),
            )
        coEvery { tableOperationsClient.getGenerationId(tempTableName) } returns 2L

        val loader =
            DirectLoadTableAppendTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
            )

        loader.start()

        coVerify(exactly = 1) {
            tableOperationsClient.createTempTable(
                stream,
                tempTableName,
                columnNameMapping,
                replace = true,
            )
        }
        coVerify(exactly = 0) {
            schemaEvolutionClient.ensureSchemaMatches(stream, tempTableName, columnNameMapping)
        }
    }

    @Test
    fun `DedupTruncateStreamLoader overwrites a table from a higher generation`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = null,
            )
        coEvery { tableOperationsClient.getGenerationId(realTableName) } returns 2L

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
                tempTableNameGenerator = tempTableNameGenerator,
            )

        loader.start()
        loader.teardown(completedSuccessfully = true)

        coVerify(exactly = 1) {
            tableOperationsClient.createTempTable(
                stream,
                tempTempTableName,
                columnNameMapping,
                replace = true,
            )
        }
        coVerify(exactly = 1) {
            tableOperationsClient.overwriteTable(
                sourceTableName = tempTempTableName,
                targetTableName = realTableName,
            )
        }
    }

    @Test
    fun `AppendTruncateStreamLoader teardown overwrites real table with temp on success`() =
        runTest {
            val initialStatus =
                DirectLoadInitialStatus(
                    realTable = DirectLoadTableStatus(isEmpty = true),
                    tempTable = DirectLoadTableStatus(isEmpty = true),
                )

            val loader =
                DirectLoadTableAppendTruncateStreamLoader(
                    stream = stream,
                    initialStatus = initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping = columnNameMapping,
                    schemaEvolutionClient = schemaEvolutionClient,
                    tableOperationsClient = tableOperationsClient,
                    streamStateStore = streamStateStore,
                )

            loader.start()
            loader.teardown(completedSuccessfully = true)

            coVerify(exactly = 1) {
                tableOperationsClient.overwriteTable(
                    sourceTableName = tempTableName,
                    targetTableName = realTableName,
                )
            }
            // No explicit dropTable needed: overwriteTable consumes the source table
            // (drops/renames it), so temp is already gone.
            coVerify(exactly = 0) { tableOperationsClient.dropTable(any()) }
        }

    @Test
    fun `AppendTruncateStreamLoader teardown does not drop temp table on failure`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = true),
                tempTable = DirectLoadTableStatus(isEmpty = true),
            )

        val loader =
            DirectLoadTableAppendTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
            )

        loader.start()
        loader.teardown(completedSuccessfully = false)

        coVerify(exactly = 0) { tableOperationsClient.overwriteTable(any(), any()) }
        coVerify(exactly = 0) { tableOperationsClient.dropTable(any()) }
    }

    @Test
    fun `DedupTruncateStreamLoader performUpsertWithTemporaryTable drops temp table after overwrite`() =
        runTest {
            // When temp table already exists with matching generation ID,
            // shouldCheckRealTableGeneration=false, so performUpsertWithTemporaryTable is called.
            val initialStatus =
                DirectLoadInitialStatus(
                    realTable = DirectLoadTableStatus(isEmpty = false),
                    tempTable = DirectLoadTableStatus(isEmpty = false),
                )

            coEvery { tableOperationsClient.getGenerationId(tempTableName) } returns 1L

            val loader =
                DirectLoadTableDedupTruncateStreamLoader(
                    stream = stream,
                    initialStatus = initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping = columnNameMapping,
                    schemaEvolutionClient = schemaEvolutionClient,
                    tableOperationsClient = tableOperationsClient,
                    streamStateStore = streamStateStore,
                    tempTableNameGenerator = tempTableNameGenerator,
                )

            loader.start()
            loader.teardown(completedSuccessfully = true)

            // Verify the performUpsertWithTemporaryTable path was taken
            coVerify(exactly = 1) {
                tableOperationsClient.createTempTable(
                    stream,
                    tempTempTableName,
                    columnNameMapping,
                    replace = true,
                )
            }
            coVerify(exactly = 1) {
                tableOperationsClient.upsertTable(
                    stream,
                    columnNameMapping,
                    sourceTableName = tempTableName,
                    targetTableName = tempTempTableName,
                )
            }
            coVerify(exactly = 1) {
                tableOperationsClient.overwriteTable(
                    sourceTableName = tempTempTableName,
                    targetTableName = realTableName,
                )
            }
            // The key assertion: temp table is dropped after the overwrite
            coVerify(exactly = 1) { tableOperationsClient.dropTable(tempTableName) }
        }

    @Test
    fun `DedupTruncateStreamLoader performDirectUpsert also drops temp table`() = runTest {
        // When no temp table exists initially, shouldCheckRealTableGeneration=true.
        // When real table doesn't exist, shouldUpsertDirectly=true.
        // This triggers the performDirectUpsert path.
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = null,
                tempTable = null,
            )

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
                tempTableNameGenerator = tempTableNameGenerator,
            )

        loader.start()
        loader.teardown(completedSuccessfully = true)

        // Verify the performDirectUpsert path was taken (creates real table, upserts, drops temp)
        coVerify(exactly = 1) {
            tableOperationsClient.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName = tempTableName,
                targetTableName = realTableName,
            )
        }
        coVerify(exactly = 1) { tableOperationsClient.dropTable(tempTableName) }
    }

    @Test
    fun `DedupTruncateStreamLoader teardown does not drop temp table on failure`() = runTest {
        val initialStatus =
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = false),
            )

        coEvery { tableOperationsClient.getGenerationId(tempTableName) } returns 1L

        val loader =
            DirectLoadTableDedupTruncateStreamLoader(
                stream = stream,
                initialStatus = initialStatus,
                realTableName = realTableName,
                tempTableName = tempTableName,
                columnNameMapping = columnNameMapping,
                schemaEvolutionClient = schemaEvolutionClient,
                tableOperationsClient = tableOperationsClient,
                streamStateStore = streamStateStore,
                tempTableNameGenerator = tempTableNameGenerator,
            )

        loader.start()
        loader.teardown(completedSuccessfully = false)

        // On failure, nothing should happen - temp table preserved for retry
        coVerify(exactly = 0) { tableOperationsClient.upsertTable(any(), any(), any(), any()) }
        coVerify(exactly = 0) { tableOperationsClient.overwriteTable(any(), any()) }
        coVerify(exactly = 0) { tableOperationsClient.dropTable(any()) }
    }
}
