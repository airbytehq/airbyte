/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlob
import io.airbyte.cdk.load.file.azureBlobStorage.AzureBlobClient
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLBulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.mockk.coEvery
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import javax.sql.DataSource
import kotlin.time.Duration.Companion.milliseconds
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

/**
 * With socket data channels, records for a stream can reach the loader pipeline on one channel
 * before the stream loader's `start()` (running on another channel) has populated the
 * [StreamStateStore]. These tests pin that the loaders wait for the stream state instead of
 * failing.
 */
class MSSQLLoaderStreamStateAwaitTest {
    private val stream =
        DestinationStream(
            unmappedNamespace = "PREPROD_IHASCO",
            unmappedName = "users",
            importType = Append,
            schema = ObjectType(properties = linkedMapOf("id" to FieldType(StringType, true))),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 0,
            namespaceMapper = NamespaceMapper(),
        )
    private val descriptor = stream.mappedDescriptor

    private lateinit var stateStore: StreamStateStore<MSSQLStreamState>
    private lateinit var dataSource: DataSource
    private lateinit var connection: Connection
    private lateinit var preparedStatement: PreparedStatement

    @BeforeEach
    fun setUp() {
        stateStore = StreamStateStore()
        dataSource = mockk()
        connection = mockk(relaxed = true)
        preparedStatement = mockk(relaxed = true)
        every { dataSource.connection } returns connection
        every { connection.autoCommit = any() } just runs
        every { connection.prepareStatement(any()) } returns preparedStatement
    }

    @Test
    fun `direct loader created before stream state is available waits for it on first record`() {
        val config =
            mockk<MSSQLConfiguration>(relaxed = true) {
                every { batchEveryNRecords } returns 5_000
                every { maxBatchSizeBytes } returns Long.MAX_VALUE
                every { numInputPartitions } returns 1
                every { maxNumOpenLoaders } returns 8
            }
        val sqlBuilder = mockk<MSSQLQueryBuilder>(relaxed = true)
        every { sqlBuilder.getFinalTableInsertColumnHeader() } returns
            "INSERT INTO [x].[y] VALUES (?)"
        val factory = MSSQLDirectLoaderFactory(config, stateStore)

        // Another socket channel creates the loader before the stream loader has started.
        val loader = factory.create(descriptor, 0)

        val result = runBlocking {
            val accepted = async {
                loader.accept(mockk<DestinationRecordRaw>(relaxed = true))
            }
            delay(200)
            stateStore.put(descriptor, MSSQLDirectLoaderStreamState(dataSource, sqlBuilder))
            accepted.await()
        }

        assertSame(io.airbyte.cdk.load.write.DirectLoader.Incomplete, result)
        verify(exactly = 1) { preparedStatement.addBatch() }
        runBlocking { loader.finish() }
        loader.close()
        verify(exactly = 1) { connection.close() }
    }

    @Test
    fun `direct loader closed before any record does not require stream state`() {
        val config = mockk<MSSQLConfiguration>(relaxed = true)
        val factory = MSSQLDirectLoaderFactory(config, stateStore)

        factory.create(descriptor, 0).close()

        verify(exactly = 0) { dataSource.connection }
    }

    @Test
    fun `bulk loader created before stream state is available waits for it on first load`() {
        val catalog = mockk<DestinationCatalog> { every { getStream(descriptor) } returns stream }
        val config = mockk<MSSQLConfiguration>(relaxed = true) { every { schema } returns "dbo" }
        val bulkLoadConfig =
            mockk<MSSQLBulkLoadConfiguration>(relaxed = true) {
                every { dataSource } returns "MyBlobDataSource"
            }
        val azureBlobClient = mockk<AzureBlobClient>()
        coEvery { azureBlobClient.delete(any<String>()) } just runs
        val factory =
            MSSQLBulkLoaderFactory(azureBlobClient, catalog, config, bulkLoadConfig, stateStore)

        // Another socket channel creates the loader before the stream loader has started.
        val loader = factory.create(StreamKey(descriptor), 0)

        runBlocking {
            val loaded = async {
                loader.load(AzureBlob("container/data.csv", mockk(relaxed = true)))
            }
            delay(200)
            stateStore.put(descriptor, MSSQLBulkLoaderStreamState(dataSource, "container/fmt.xml"))
            loaded.await()
        }

        val sqlStatements = mutableListOf<String>()
        verify(atLeast = 1) { connection.prepareStatement(capture(sqlStatements)) }
        val bulkInsert = sqlStatements.single { it.contains("BULK INSERT") }
        assertTrue(bulkInsert.contains("FROM 'container/data.csv'"), bulkInsert)
        assertTrue(bulkInsert.contains("FORMATFILE = 'container/fmt.xml'"), bulkInsert)
    }

    @Test
    fun `awaiting stream state times out with a descriptive error`() {
        val exception =
            assertThrows(IllegalStateException::class.java) {
                runBlocking { stateStore.awaitStreamState(descriptor, timeout = 100.milliseconds) }
            }
        assertEquals(
            "Timed out after 100ms waiting for stream $descriptor to be initialized.",
            exception.message,
        )
    }
}
