/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.write.StreamStateStore
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test

class DirectLoadTableStreamLoaderTest {

    private val stream =
        mockk<DestinationStream>(relaxed = true) {
            every { mappedDescriptor } returns
                DestinationStream.Descriptor("test_namespace", "test_stream")
            every { minimumGenerationId } returns 1L
        }
    private val realTableName = TableName("real_namespace", "real_table")
    private val tempTableName = TableName("temp_namespace", "temp_table")
    private val tempTempTableName = TableName("temp_namespace", "temp_temp_table")
    private val columnNameMapping = ColumnNameMapping(emptyMap())
    private val nativeTableOperations = mockk<DirectLoadTableNativeOperations>(relaxed = true)
    private val sqlTableOperations = mockk<DirectLoadTableSqlOperations>(relaxed = true)
    private val streamStateStore = StreamStateStore<DirectLoadTableExecutionConfig>()
    private val tempTableNameGenerator =
        mockk<TempTableNameGenerator> {
            every { generate(tempTableName) } returns tempTempTableName
        }

    @Test
    fun `DedupTruncateStreamLoader directly upserts when real table has current generation`() =
        runBlocking {
            val initialStatus =
                DirectLoadInitialStatus(
                    realTable = DirectLoadTableStatus(isEmpty = false),
                    tempTable = DirectLoadTableStatus(isEmpty = true),
                )

            coEvery { nativeTableOperations.getGenerationId(realTableName) } returns 1L

            val loader =
                DirectLoadTableDedupTruncateStreamLoader(
                    stream = stream,
                    initialStatus = initialStatus,
                    realTableName = realTableName,
                    tempTableName = tempTableName,
                    columnNameMapping = columnNameMapping,
                    nativeTableOperations = nativeTableOperations,
                    sqlTableOperations = sqlTableOperations,
                    streamStateStore = streamStateStore,
                    tempTableNameGenerator = tempTableNameGenerator,
                )

            loader.start()
            loader.close(hadNonzeroRecords = false, streamFailure = null)

            coVerify(exactly = 0) {
                sqlTableOperations.createTable(
                    stream,
                    tempTempTableName,
                    columnNameMapping,
                    replace = true,
                )
            }
            coVerify(exactly = 1) {
                sqlTableOperations.upsertTable(
                    stream,
                    columnNameMapping,
                    sourceTableName = tempTableName,
                    targetTableName = realTableName,
                )
            }
            coVerify(exactly = 0) { sqlTableOperations.overwriteTable(any(), any()) }
            coVerify(exactly = 1) { sqlTableOperations.dropTable(tempTableName) }
        }
}
