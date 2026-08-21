/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.cdk.load.write.StreamStateStore
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class DirectLoadTableWriterTest {
    @Test
    fun setupRejectsAllDedupeStreamsWithoutPrimaryKeys() {
        val writer =
            writerFor(
                stream("first", Dedupe(emptyList(), emptyList())),
                stream("second", Dedupe(emptyList(), emptyList())),
            )

        val exception = assertThrows<ConfigErrorException> { runBlocking { writer.setup() } }

        assertTrue(exception.message!!.contains("namespace.first"))
        assertTrue(exception.message!!.contains("namespace.second"))
    }

    @Test
    fun setupAllowsDedupeWithPrimaryKey() {
        val writer = writerFor(stream("keyed", Dedupe(listOf(listOf("id")), emptyList())))

        assertDoesNotThrow { runBlocking { writer.setup() } }
    }

    @Test
    fun setupAllowsAppend() {
        val writer = writerFor(stream("append", Append))

        assertDoesNotThrow { runBlocking { writer.setup() } }
    }

    private fun writerFor(vararg streams: DestinationStream): DirectLoadTableWriter {
        val names =
            TableCatalog(
                streams.associateWith { stream ->
                    TableNameInfo(
                        TableNames(
                            rawTableName = null,
                            finalTableName = TableName("namespace", stream.mappedDescriptor.name),
                        ),
                        ColumnNameMapping(emptyMap()),
                    )
                }
            )
        val stateGatherer = mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>>()
        coEvery { stateGatherer.gatherInitialStatus(any()) } returns emptyMap()
        return DirectLoadTableWriter(
            internalNamespace = "airbyte_internal",
            names = names,
            stateGatherer = stateGatherer,
            destinationHandler = mockk<DatabaseHandler>(relaxed = true),
            nativeTableOperations = mockk<DirectLoadTableNativeOperations>(relaxed = true),
            sqlTableOperations = mockk<DirectLoadTableSqlOperations>(relaxed = true),
            streamStateStore =
                mockk<StreamStateStore<DirectLoadTableExecutionConfig>>(relaxed = true),
            tempTableNameGenerator = mockk<TempTableNameGenerator>(relaxed = true),
        )
    }

    private fun stream(name: String, importType: ImportType): DestinationStream = mockk {
        every { this@mockk.importType } returns importType
        every { this@mockk.mappedDescriptor } returns
            DestinationStream.Descriptor("namespace", name)
    }
}
