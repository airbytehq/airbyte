/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
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
                tempTableNameGenerator = mockk()
            )

        runBlocking { writer.setup() }

        coVerify(exactly = 1) {
            snowflakeClient.createNamespace(tableName.namespace.toSnowflakeCompatibleName())
        }
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
                tempTableNameGenerator = tempTableNameGenerator
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
                tempTableNameGenerator = tempTableNameGenerator
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
                tempTableNameGenerator = tempTableNameGenerator
            )

        runBlocking {
            writer.setup()
            assertThrows(SystemErrorException::class.java) { writer.createStreamLoader(stream) }
        }
    }
}
