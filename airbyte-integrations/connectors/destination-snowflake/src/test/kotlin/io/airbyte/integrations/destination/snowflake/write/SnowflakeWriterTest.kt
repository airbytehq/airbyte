/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.schema.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

internal class SnowflakeWriterTest {

    @Test
    fun testSetup() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream = mockk<DestinationStream>()
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus(catalog) } returns emptyMap()
            }
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration = mockk(relaxed = true),
            )

        runBlocking { writer.setup() }

        coVerify(exactly = 1) { snowflakeClient.createNamespace(tableName.namespace) }
        coVerify(exactly = 1) { stateGatherer.gatherInitialStatus(catalog) }
    }

    @Test
    fun testCreateStreamLoaderFirstGeneration() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
                every { importType } returns Append
            }
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus(catalog) } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null,
                            )
                    )
            }
        val tempTableNameGenerator =
            mockk<TempTableNameGenerator> { every { generate(any()) } answers { firstArg() } }
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration = mockk(relaxed = true),
            )

        runBlocking {
            writer.setup()
            val streamLoader = writer.createStreamLoader(stream)
            assertEquals(DirectLoadTableAppendStreamLoader::class, streamLoader::class)
        }
    }

    @Test
    fun testCreateStreamLoaderNotFirstGeneration() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 1L
                every { generationId } returns 1L
                every { importType } returns Append
            }
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus(catalog) } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null,
                            )
                    )
            }
        val tempTableNameGenerator =
            mockk<TempTableNameGenerator> { every { generate(any()) } answers { firstArg() } }
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration = mockk(relaxed = true),
            )

        runBlocking {
            writer.setup()
            val streamLoader = writer.createStreamLoader(stream)
            assertEquals(DirectLoadTableAppendTruncateStreamLoader::class, streamLoader::class)
        }
    }

    @Test
    fun testCreateStreamLoaderHybrid() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 1L
                every { generationId } returns 2L
            }
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus(catalog) } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null,
                            )
                    )
            }
        val tempTableNameGenerator =
            mockk<TempTableNameGenerator> { every { generate(any()) } answers { firstArg() } }
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration = mockk(relaxed = true),
            )

        runBlocking {
            writer.setup()
            assertThrows(SystemErrorException::class.java) { writer.createStreamLoader(stream) }
        }
    }

    @Test
    fun testSetupWithNamespaceCreationFailure() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream = mockk<DestinationStream>()
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>()
        val stateGatherer = mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>>()
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration = mockk(),
            )

        // Simulate network failure during namespace creation
        coEvery {
            snowflakeClient.createNamespace(tableName.namespace.toSnowflakeCompatibleName())
        } throws RuntimeException("Network connection failed")

        assertThrows(RuntimeException::class.java) { runBlocking { writer.setup() } }
    }

    @Test
    fun testSetupWithInitialStatusGatheringFailure() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream = mockk<DestinationStream>()
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer = mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>>()
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration = mockk(),
            )

        // Simulate failure while gathering initial status
        coEvery { stateGatherer.gatherInitialStatus(catalog) } throws
            RuntimeException("Failed to query table status")

        assertThrows(RuntimeException::class.java) { runBlocking { writer.setup() } }

        // Verify namespace creation was still attempted
        coVerify(exactly = 1) { snowflakeClient.createNamespace(tableName.namespace) }
    }

    @Test
    fun testCreateStreamLoaderWithMissingInitialStatus() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tableNames = TableNames(rawTableName = null, finalTableName = tableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
            }
        val missingStream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
            }
        val tableInfo =
            TableNameInfo(
                tableNames = tableNames,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream to tableInfo))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus(catalog) } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null,
                            )
                    )
            }
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration = mockk(relaxed = true),
            )

        runBlocking {
            writer.setup()
            // Try to create loader for a stream that wasn't in initial status
            assertThrows(NullPointerException::class.java) {
                writer.createStreamLoader(missingStream)
            }
        }
    }

    @Test
    fun testCreateStreamLoaderWithNullFinalTableName() {
        // TableNames constructor throws IllegalStateException when both names are null
        assertThrows(IllegalStateException::class.java) {
            TableNames(rawTableName = null, finalTableName = null)
        }
    }

    @Test
    fun testSetupWithMultipleNamespaceFailuresPartial() {
        val tableName1 = TableName(namespace = "namespace1", name = "table1")
        val tableName2 = TableName(namespace = "namespace2", name = "table2")
        val tableNames1 = TableNames(rawTableName = null, finalTableName = tableName1)
        val tableNames2 = TableNames(rawTableName = null, finalTableName = tableName2)
        val stream1 = mockk<DestinationStream>()
        val stream2 = mockk<DestinationStream>()
        val tableInfo1 =
            TableNameInfo(
                tableNames = tableNames1,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val tableInfo2 =
            TableNameInfo(
                tableNames = tableNames2,
                columnNameMapping = ColumnNameMapping(emptyMap())
            )
        val catalog = TableCatalog(mapOf(stream1 to tableInfo1, stream2 to tableInfo2))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>()
        val stateGatherer = mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>>()
        val writer =
            SnowflakeWriter(
                names = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = mockk(),
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration = mockk(),
            )

        // First namespace succeeds, second fails (namespaces are uppercased by
        // toSnowflakeCompatibleName)
        coEvery { snowflakeClient.createNamespace("namespace1") } returns Unit
        coEvery { snowflakeClient.createNamespace("namespace2") } throws
            RuntimeException("Connection timeout")

        assertThrows(RuntimeException::class.java) { runBlocking { writer.setup() } }

        // Verify both namespace creations were attempted
        coVerify(exactly = 1) { snowflakeClient.createNamespace("namespace1") }
        coVerify(exactly = 1) { snowflakeClient.createNamespace("namespace2") }
    }
}
