/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.load.table.directload.DirectLoadInitialStatus
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableAppendTruncateStreamLoader
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.table.directload.DirectLoadTableStatus
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
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
        val tempTableName = TableName(namespace = "test-namespace", name = "test-name-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
                every { importType } returns Append
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null
                            )
                    )
            }
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { internalTableSchema } returns "internal_schema"
                    },
            )

        runBlocking { writer.setup() }

        coVerify(exactly = 1) { snowflakeClient.createNamespace(tableName.namespace) }
        coVerify(exactly = 1) { stateGatherer.gatherInitialStatus() }
    }

    @Test
    fun testCreateStreamLoaderFirstGeneration() {
        val tableName = TableName(namespace = "test-namespace", name = "test-name")
        val tempTableName = TableName(namespace = "test-namespace", name = "test-name-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
                every { importType } returns Append
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
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
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { internalTableSchema } returns "internal_schema"
                    },
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
        val tempTableName = TableName(namespace = "test-namespace", name = "test-name-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 1L
                every { generationId } returns 1L
                every { importType } returns Append
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
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
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { internalTableSchema } returns "internal_schema"
                    },
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
        val tempTableName = TableName(namespace = "test-namespace", name = "test-name-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 1L
                every { generationId } returns 2L
                every { importType } returns Append
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
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
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = tempTableNameGenerator,
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { internalTableSchema } returns "internal_schema"
                    },
            )

        runBlocking {
            writer.setup()
            assertThrows(SystemErrorException::class.java) { writer.createStreamLoader(stream) }
        }
    }

    @Test
    fun testCreateStreamLoaderNamespaceLegacy() {
        val namespace = "test-namespace"
        val name = "test-name"
        val tableName = TableName(namespace = namespace, name = name)
        val tempTableName = TableName(namespace = namespace, name = "${name}-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
                every { importType } returns Append
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null
                            )
                    )
            }
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { legacyRawTablesOnly } returns true
                        every { internalTableSchema } returns "internal_schema"
                    },
            )

        runBlocking { writer.setup() }

        coVerify(exactly = 1) { snowflakeClient.createNamespace(tableName.namespace) }
    }

    @Test
    fun testCreateStreamLoaderNamespaceNonLegacy() {
        val namespace = "test-namespace"
        val name = "test-name"
        val tableName = TableName(namespace = namespace, name = name)
        val tempTableName = TableName(namespace = namespace, name = "${name}-temp")
        val tableNames = TableNames(finalTableName = tableName, tempTableName = tempTableName)
        val stream =
            mockk<DestinationStream> {
                every { minimumGenerationId } returns 0L
                every { generationId } returns 0L
                every { importType } returns Append
                every { tableSchema } returns
                    StreamTableSchema(
                        tableNames = tableNames,
                        columnSchema =
                            ColumnSchema(
                                inputToFinalColumnNames = emptyMap(),
                                finalSchema = emptyMap(),
                                inputSchema = emptyMap()
                            ),
                        importType = Append
                    )
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor(
                        namespace = tableName.namespace,
                        name = tableName.name
                    )
            }
        val catalog = DestinationCatalog(listOf(stream))
        val snowflakeClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val stateGatherer =
            mockk<DatabaseInitialStatusGatherer<DirectLoadInitialStatus>> {
                coEvery { gatherInitialStatus() } returns
                    mapOf(
                        stream to
                            DirectLoadInitialStatus(
                                realTable = DirectLoadTableStatus(false),
                                tempTable = null
                            )
                    )
            }
        val streamStateStore = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
        val writer =
            SnowflakeWriter(
                catalog = catalog,
                stateGatherer = stateGatherer,
                streamStateStore = streamStateStore,
                snowflakeClient = snowflakeClient,
                tempTableNameGenerator = mockk(),
                snowflakeConfiguration =
                    mockk(relaxed = true) {
                        every { legacyRawTablesOnly } returns false
                        every { internalTableSchema } returns "internal_schema"
                    },
            )

        runBlocking { writer.setup() }

        coVerify(exactly = 1) { snowflakeClient.createNamespace(namespace) }
    }
}
