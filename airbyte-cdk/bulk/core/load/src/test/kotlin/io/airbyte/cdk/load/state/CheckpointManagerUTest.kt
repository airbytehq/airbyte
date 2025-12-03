/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.mockk.Ordering
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.just
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class CheckpointManagerUTest {
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) lateinit var syncManager: SyncManager
    private val outputConsumer: suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit =
        mockk<suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit>(relaxed = true)
    @MockK(relaxed = true) lateinit var timeProvider: TimeProvider
    @MockK(relaxed = true) lateinit var streamManager1: StreamManager
    @MockK(relaxed = true) lateinit var streamManager2: StreamManager

    private val stream1 =
        DestinationStream(
            unmappedNamespace = "test",
            unmappedName = "stream1",
            importType = Append,
            schema = ObjectTypeWithEmptySchema,
            generationId = 10L,
            minimumGenerationId = 10L,
            syncId = 101L,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                io.airbyte.cdk.load.schema.model.StreamTableSchema(
                    tableNames =
                        io.airbyte.cdk.load.schema.model.TableNames(
                            finalTableName =
                                io.airbyte.cdk.load.schema.model.TableName("test", "stream1")
                        ),
                    columnSchema =
                        io.airbyte.cdk.load.schema.model.ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                )
        )

    private val stream2 =
        DestinationStream(
            unmappedNamespace = "test",
            unmappedName = "stream2",
            importType = Append,
            schema = ObjectTypeWithEmptySchema,
            generationId = 10L,
            minimumGenerationId = 10L,
            syncId = 101L,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                io.airbyte.cdk.load.schema.model.StreamTableSchema(
                    tableNames =
                        io.airbyte.cdk.load.schema.model.TableNames(
                            finalTableName =
                                io.airbyte.cdk.load.schema.model.TableName("test", "stream2")
                        ),
                    columnSchema =
                        io.airbyte.cdk.load.schema.model.ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                )
        )

    @BeforeEach
    fun setup() {
        coEvery { catalog.streams } returns listOf(stream1, stream2)
        coEvery { outputConsumer.invoke(any(), any(), any(), any()) } returns Unit
        coEvery { syncManager.getStreamManager(stream1.mappedDescriptor) } returns streamManager1
        coEvery { syncManager.getStreamManager(stream2.mappedDescriptor) } returns streamManager2
    }

    private fun makeCheckpointManager(): CheckpointManager {
        return CheckpointManager(
            catalog,
            syncManager,
            outputConsumer,
            timeProvider,
            true,
            NamespaceMapper(NamespaceDefinitionType.SOURCE)
        )
    }

    private fun makeKey(index: Int, id: String? = null) =
        CheckpointKey(
            checkpointIndex = CheckpointIndex(index),
            checkpointId = CheckpointId(id ?: index.toString())
        )

    @Test
    fun `test checkpoint-by-id`() = runTest {
        val checkpointManager = makeCheckpointManager()

        val message1 = mockMessage()
        val message2 = mockMessage()

        checkpointManager.addStreamCheckpoint(stream1.mappedDescriptor, makeKey(1), message1)
        checkpointManager.addStreamCheckpoint(stream2.mappedDescriptor, makeKey(1), message2)

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("1")) } returns false
        coEvery { streamManager2.areRecordsPersistedForCheckpoint(CheckpointId("1")) } returns true

        // Only stream2 should be flushed.
        checkpointManager.flushReadyCheckpointMessages()
        coVerify(exactly = 0) { outputConsumer.invoke(message1, any(), any(), any()) }
        coVerify(exactly = 1) { outputConsumer.invoke(message2, any(), any(), any()) }
    }

    @Test
    fun `checkpoint N will not be emitted before N-1`() = runTest {
        val checkpointManager = makeCheckpointManager()

        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(1, "one"),
            mockk(relaxed = true)
        )
        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(2, "two"),
            mockk(relaxed = true)
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            false
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            true

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 0) { outputConsumer.invoke(any(), any(), any(), any()) }
    }

    @Test
    fun `checkpoint N will be emitted after N-1`() = runTest {
        val checkpointManager = makeCheckpointManager()
        val message1 = mockMessage()
        val message2 = mockMessage()

        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(1, "one"),
            message1,
        )
        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(2, "two"),
            message2,
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            true
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            true

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(ordering = Ordering.ORDERED) {
            outputConsumer.invoke(message1, any(), any(), any())
            outputConsumer.invoke(message2, any(), any(), any())
        }
    }

    @Test
    fun `checkpoints will be emitted in order even if received out of order`() = runTest {
        val checkpointManager = makeCheckpointManager()
        val message1 = mockMessage()
        val message2 = mockMessage()

        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(2, "two"),
            message2,
        )
        checkpointManager.addStreamCheckpoint(
            stream1.mappedDescriptor,
            makeKey(1, "one"),
            message1,
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            true
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            false

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 1) { outputConsumer.invoke(message1, any(), any(), any()) }
    }

    @Test
    fun testGlobalSnapshotCheckpoints() = runTest {
        val checkpointManager = makeCheckpointManager()
        val checkpointKey1 = makeKey(1, "one")
        val checkpointKey2 = makeKey(2, "two")
        val checkpointKey3 = makeKey(3, "three")
        val globalSnapshotCheckpoint1 =
            mockk<GlobalSnapshotCheckpoint> {
                every { streamCheckpoints } returns
                    mapOf(stream1.mappedDescriptor to checkpointKey3)
                every { sourceStats } returns CheckpointMessage.Stats(0)
                every { updateStats(any()) } just Runs
                every { checkpoints } returns emptyList()
            }
        val globalSnapshotCheckpoint2 =
            mockk<GlobalSnapshotCheckpoint> {
                every { streamCheckpoints } returns
                    mapOf(stream2.mappedDescriptor to checkpointKey2)
                every { sourceStats } returns CheckpointMessage.Stats(0)
                every { updateStats(any()) } just Runs
                every { checkpoints } returns emptyList()
            }
        val message1 = mockMessage(globalSnapshotCheckpoint1)
        val message2 = mockMessage(globalSnapshotCheckpoint2)

        coEvery {
            streamManager1.areRecordsPersistedForCheckpoint(checkpointKey3.checkpointId)
        } returns true
        coEvery {
            streamManager2.areRecordsPersistedForCheckpoint(checkpointKey2.checkpointId)
        } returns true

        checkpointManager.addGlobalCheckpoint(checkpointKey2, message2)

        checkpointManager.addGlobalCheckpoint(checkpointKey1, message1)

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 1) { outputConsumer.invoke(message1, any(), any(), any()) }
        coVerify(exactly = 1) { outputConsumer.invoke(message2, any(), any(), any()) }
    }

    @Test
    fun testGlobalSnapshotCheckpointsOnlyOneStreamUpToDate() = runTest {
        val checkpointManager = makeCheckpointManager()
        val checkpointKey1 = makeKey(1, "one")
        val checkpointKey2 = makeKey(2, "two")
        val checkpointKey3 = makeKey(3, "three")
        val globalSnapshotCheckpoint1 =
            mockk<GlobalSnapshotCheckpoint> {
                every { streamCheckpoints } returns
                    mapOf(stream1.mappedDescriptor to checkpointKey3)
                every { sourceStats } returns CheckpointMessage.Stats(0)
            }
        val globalSnapshotCheckpoint2 =
            mockk<GlobalSnapshotCheckpoint> {
                every { streamCheckpoints } returns
                    mapOf(stream2.mappedDescriptor to checkpointKey2)
                every { sourceStats } returns CheckpointMessage.Stats(0)
            }
        val message1 = mockMessage(globalSnapshotCheckpoint1)
        val message2 = mockMessage(globalSnapshotCheckpoint2)

        coEvery {
            streamManager1.areRecordsPersistedForCheckpoint(checkpointKey3.checkpointId)
        } returns false
        coEvery {
            streamManager2.areRecordsPersistedForCheckpoint(checkpointKey2.checkpointId)
        } returns false

        checkpointManager.addGlobalCheckpoint(checkpointKey2, message2)

        checkpointManager.addGlobalCheckpoint(checkpointKey1, message1)

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 0) { outputConsumer.invoke(any(), any(), any(), any()) }
    }

    private fun mockMessage(
        checkpointMessage: CheckpointMessage? = null
    ): Reserved<CheckpointMessage> = Reserved(value = checkpointMessage ?: mockk(relaxed = true))
}
