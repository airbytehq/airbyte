/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableDedupStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class PostgresWriterTest {

    private lateinit var writer: PostgresWriter
    private lateinit var names: TableCatalog
    private lateinit var stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>
    private lateinit var streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>
    private lateinit var postgresClient: PostgresAirbyteClient
    private lateinit var tempTableNameGenerator: TempTableNameGenerator
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setup() {
        names = mockk()
        stateGatherer = mockk()
        streamStateStore = mockk()
        postgresClient = mockk()
        tempTableNameGenerator = mockk()
        postgresConfiguration = mockk()

        writer =
            PostgresWriter(
                names,
                stateGatherer,
                streamStateStore,
                postgresClient,
                tempTableNameGenerator,
                postgresConfiguration
            )
    }

    @Test
    fun `test createStreamLoader with normal mode and Dedupe`() = runBlocking {
        every { postgresConfiguration.legacyRawTablesOnly } returns false

        val stream = mockk<DestinationStream>()
        val finalTableName = TableName("ns", "name")
        val mapping = mockk<ColumnNameMapping>(relaxed = true)

        val tableNameInfo = mockk<TableNameInfo>(relaxed = true)
        every { tableNameInfo.tableNames.finalTableName } returns finalTableName
        every { tableNameInfo.columnNameMapping } returns mapping
        every { tableNameInfo.component1() } answers { tableNameInfo.tableNames }
        every { tableNameInfo.component2() } answers { tableNameInfo.columnNameMapping }

        every { stream.importType } returns Dedupe(primaryKey = emptyList(), cursor = emptyList())
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        // Mock names map behavior
        val namesMap = mapOf(stream to tableNameInfo)
        every { names.values } returns namesMap.values
        every { names[stream] } returns tableNameInfo

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus(names) } returns mapOf(stream to initialStatus)

        every { tempTableNameGenerator.generate(finalTableName) } returns
            TableName("ns", "temp_name")

        writer.setup()
        val loader = writer.createStreamLoader(stream)

        assertTrue(loader is DirectLoadTableDedupStreamLoader)
    }

    @Test
    fun `test createStreamLoader with raw mode and Dedupe`() = runBlocking {
        every { postgresConfiguration.legacyRawTablesOnly } returns true

        val stream = mockk<DestinationStream>()
        val finalTableName = TableName("ns", "name")
        val mapping = mockk<ColumnNameMapping>(relaxed = true)

        val tableNameInfo = mockk<TableNameInfo>(relaxed = true)
        every { tableNameInfo.tableNames.finalTableName } returns finalTableName
        every { tableNameInfo.columnNameMapping } returns mapping
        every { tableNameInfo.component1() } answers { tableNameInfo.tableNames }
        every { tableNameInfo.component2() } answers { tableNameInfo.columnNameMapping }

        every { stream.importType } returns Dedupe(primaryKey = emptyList(), cursor = emptyList())
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        // Mock names map behavior
        val namesMap = mapOf(stream to tableNameInfo)
        every { names.values } returns namesMap.values
        every { names[stream] } returns tableNameInfo

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus(names) } returns mapOf(stream to initialStatus)

        every { tempTableNameGenerator.generate(finalTableName) } returns
            TableName("ns", "temp_name")

        writer.setup()
        val loader = writer.createStreamLoader(stream)

        assertTrue(
            loader is DirectLoadTableAppendStreamLoader,
            "Should use Append loader in raw mode even if importType is Dedupe"
        )
    }

    @Test
    fun `test createStreamLoader with raw mode and Append`() = runBlocking {
        every { postgresConfiguration.legacyRawTablesOnly } returns true

        val stream = mockk<DestinationStream>()
        val finalTableName = TableName("ns", "name")
        val mapping = mockk<ColumnNameMapping>(relaxed = true)

        val tableNameInfo = mockk<TableNameInfo>(relaxed = true)
        every { tableNameInfo.tableNames.finalTableName } returns finalTableName
        every { tableNameInfo.columnNameMapping } returns mapping
        every { tableNameInfo.component1() } answers { tableNameInfo.tableNames }
        every { tableNameInfo.component2() } answers { tableNameInfo.columnNameMapping }

        // Use a mock for ImportType that is NOT Dedupe
        val appendImportType = mockk<ImportType>()
        every { stream.importType } returns appendImportType
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        // Mock names map behavior
        val namesMap = mapOf(stream to tableNameInfo)
        every { names.values } returns namesMap.values
        every { names[stream] } returns tableNameInfo

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus(names) } returns mapOf(stream to initialStatus)

        every { tempTableNameGenerator.generate(finalTableName) } returns
            TableName("ns", "temp_name")

        writer.setup()
        val loader = writer.createStreamLoader(stream)

        assertTrue(loader is DirectLoadTableAppendStreamLoader)
    }
}
