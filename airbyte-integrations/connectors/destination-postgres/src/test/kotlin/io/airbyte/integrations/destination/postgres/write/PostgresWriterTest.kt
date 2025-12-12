/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableDedupStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
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
    private lateinit var catalog: DestinationCatalog
    private lateinit var stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>
    private lateinit var streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>
    private lateinit var postgresClient: PostgresAirbyteClient
    private lateinit var tempTableNameGenerator: TempTableNameGenerator
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setup() {
        catalog = mockk()
        stateGatherer = mockk()
        streamStateStore = mockk()
        postgresClient = mockk()
        tempTableNameGenerator = mockk()
        postgresConfiguration = mockk()

        writer =
            PostgresWriter(
                catalog,
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

        val tableNames = TableNames(finalTableName = finalTableName)
        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema = emptyMap()
            )
        val importType = Dedupe(primaryKey = emptyList(), cursor = emptyList())
        val tableSchema = StreamTableSchema(tableNames, columnSchema, importType)

        every { stream.tableSchema } returns tableSchema
        every { stream.importType } returns importType
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        every { catalog.streams } returns listOf(stream)

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus() } returns mapOf(stream to initialStatus)

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

        val tableNames = TableNames(finalTableName = finalTableName)
        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema = emptyMap()
            )
        val importType = Dedupe(primaryKey = emptyList(), cursor = emptyList())
        val tableSchema = StreamTableSchema(tableNames, columnSchema, importType)

        every { stream.tableSchema } returns tableSchema
        every { stream.importType } returns importType
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        every { catalog.streams } returns listOf(stream)

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus() } returns mapOf(stream to initialStatus)

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

        val tableNames = TableNames(finalTableName = finalTableName)
        val columnSchema =
            ColumnSchema(
                inputSchema = emptyMap(),
                inputToFinalColumnNames = emptyMap(),
                finalSchema = emptyMap()
            )
        // Use a mock for ImportType that is NOT Dedupe
        val appendImportType = mockk<ImportType>()
        val tableSchema = StreamTableSchema(tableNames, columnSchema, appendImportType)

        every { stream.tableSchema } returns tableSchema
        every { stream.importType } returns appendImportType
        every { stream.minimumGenerationId } returns 0L
        every { stream.generationId } returns 1L

        every { catalog.streams } returns listOf(stream)

        coEvery { postgresClient.createNamespace(any()) } just Runs

        val initialStatus = mockk<DirectLoadInitialStatus>()
        coEvery { stateGatherer.gatherInitialStatus() } returns mapOf(stream to initialStatus)

        every { tempTableNameGenerator.generate(finalTableName) } returns
            TableName("ns", "temp_name")

        writer.setup()
        val loader = writer.createStreamLoader(stream)

        assertTrue(loader is DirectLoadTableAppendStreamLoader)
    }
}
