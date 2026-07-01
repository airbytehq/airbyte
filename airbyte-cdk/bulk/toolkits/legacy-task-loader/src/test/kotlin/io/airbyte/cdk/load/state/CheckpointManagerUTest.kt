/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import io.airbyte.cdk.load.message.GlobalCheckpoint
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
            namespaceMapper = NamespaceMapper()
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
            namespaceMapper = NamespaceMapper()
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

    /**
     * Regression coverage for airbytehq/oncall#12017: in socket mode, `checkGlobalStreams` must
     * treat records that the destination *rejected* (DLQ'd) as still accounted for when comparing
     * to the source-reported record count. Without this, a single rejected record prevents the
     * global checkpoint from ever flushing, and `awaitAllCheckpointsFlushed` busy-waits forever.
     */
    @Test
    fun `socket-mode global checkpoint flushes when some records are rejected by the destination`() =
        runTest {
            val checkpointManager = makeSocketModeCheckpointManager()
            val key = makeKey(1, "one")
            // Source emitted 10 records for this checkpoint.
            val sourceStats = CheckpointMessage.Stats(recordCount = 10)
            val globalCheckpoint =
                mockk<GlobalCheckpoint> {
                    every { this@mockk.sourceStats } returns sourceStats
                    every { checkpointKey } returns key
                    every { updateStats(any()) } just Runs
                    every { checkpoints } returns emptyList()
                    every { destinationStats } returns null
                    every { additionalProperties } returns emptyMap()
                }
            val message = mockMessage(globalCheckpoint)

            // Both streams report their records as persisted...
            coEvery { streamManager1.areRecordsPersistedForCheckpoint(key.checkpointId) } returns
                true
            coEvery { streamManager2.areRecordsPersistedForCheckpoint(key.checkpointId) } returns
                true
            // ...but 7 records committed + 3 rejected == 10 source records.
            every { streamManager1.committedCount(key.checkpointId) } returns
                CheckpointValue(records = 5, serializedBytes = 0, rejectedRecords = 2)
            every { streamManager2.committedCount(key.checkpointId) } returns
                CheckpointValue(records = 2, serializedBytes = 0, rejectedRecords = 1)

            checkpointManager.addGlobalCheckpoint(key, message)
            checkpointManager.flushReadyCheckpointMessages()

            coVerify(exactly = 1) { outputConsumer.invoke(message, any(), any(), any()) }
        }

    /**
     * Negative counterpart: if committed + rejected still does not equal the source-reported count,
     * the checkpoint must not flush. This protects against an overly permissive fix that would emit
     * checkpoints despite unaccounted-for records.
     */
    @Test
    fun `socket-mode global checkpoint does not flush when committed plus rejected is still short of source`() =
        runTest {
            val checkpointManager = makeSocketModeCheckpointManager()
            val key = makeKey(1, "one")
            val sourceStats = CheckpointMessage.Stats(recordCount = 10)
            val globalCheckpoint =
                mockk<GlobalCheckpoint> {
                    every { this@mockk.sourceStats } returns sourceStats
                    every { checkpointKey } returns key
                    every { updateStats(any()) } just Runs
                    every { checkpoints } returns emptyList()
                    every { destinationStats } returns null
                    every { additionalProperties } returns emptyMap()
                }
            val message = mockMessage(globalCheckpoint)

            coEvery { streamManager1.areRecordsPersistedForCheckpoint(key.checkpointId) } returns
                true
            coEvery { streamManager2.areRecordsPersistedForCheckpoint(key.checkpointId) } returns
                true
            every { streamManager1.committedCount(key.checkpointId) } returns
                CheckpointValue(records = 4, serializedBytes = 0, rejectedRecords = 1)
            every { streamManager2.committedCount(key.checkpointId) } returns
                CheckpointValue(records = 2, serializedBytes = 0, rejectedRecords = 1)

            checkpointManager.addGlobalCheckpoint(key, message)
            checkpointManager.flushReadyCheckpointMessages()

            coVerify(exactly = 0) { outputConsumer.invoke(any(), any(), any(), any()) }
        }

    /**
     * Regression coverage for oncall#12017 on the stream-state code path: `flushStreamCheckpoints`
     * must also count rejected records toward the source-vs-destination comparison when operating
     * in socket mode.
     */
    @Test
    fun `socket-mode stream checkpoint flushes when some records are rejected by the destination`() =
        runTest {
            val checkpointManager = makeSocketModeCheckpointManager()
            val key = makeKey(1, "one")
            val sourceStats = CheckpointMessage.Stats(recordCount = 10)
            val streamCheckpoint =
                mockk<CheckpointMessage>(relaxed = true) {
                    every { this@mockk.sourceStats } returns sourceStats
                    every { checkpointKey } returns key
                    every { updateStats(any()) } just Runs
                }
            val message = mockMessage(streamCheckpoint)

            coEvery { streamManager1.areRecordsPersistedForCheckpoint(key.checkpointId) } returns
                true
            every { streamManager1.committedCount(key.checkpointId) } returns
                CheckpointValue(records = 7, serializedBytes = 0, rejectedRecords = 3)

            checkpointManager.addStreamCheckpoint(stream1.mappedDescriptor, key, message)
            checkpointManager.flushReadyCheckpointMessages()

            coVerify(exactly = 1) { outputConsumer.invoke(message, any(), any(), any()) }
        }

    /** Regression coverage for oncall#12017 on the snapshot-checkpoint code path. */
    @Test
    fun `socket-mode snapshot checkpoint flushes when some records are rejected by the destination`() =
        runTest {
            val checkpointManager = makeSocketModeCheckpointManager()
            val innerKey1 = makeKey(2, "inner1")
            val innerKey2 = makeKey(3, "inner2")
            val outerKey = makeKey(1, "outer")
            val sourceStats = CheckpointMessage.Stats(recordCount = 10)
            val snapshot =
                mockk<GlobalSnapshotCheckpoint> {
                    every { streamCheckpoints } returns
                        mapOf(
                            stream1.mappedDescriptor to innerKey1,
                            stream2.mappedDescriptor to innerKey2,
                        )
                    every { this@mockk.sourceStats } returns sourceStats
                    every { checkpointKey } returns outerKey
                    every { updateStats(any()) } just Runs
                    every { checkpoints } returns emptyList()
                    every { destinationStats } returns null
                    every { additionalProperties } returns emptyMap()
                }
            val message = mockMessage(snapshot)

            coEvery {
                streamManager1.areRecordsPersistedForCheckpoint(innerKey1.checkpointId)
            } returns true
            coEvery {
                streamManager2.areRecordsPersistedForCheckpoint(innerKey2.checkpointId)
            } returns true
            every { streamManager1.committedCount(innerKey1.checkpointId) } returns
                CheckpointValue(records = 4, serializedBytes = 0, rejectedRecords = 2)
            every { streamManager2.committedCount(innerKey2.checkpointId) } returns
                CheckpointValue(records = 3, serializedBytes = 0, rejectedRecords = 1)

            checkpointManager.addGlobalCheckpoint(outerKey, message)
            checkpointManager.flushReadyCheckpointMessages()

            coVerify(exactly = 1) { outputConsumer.invoke(message, any(), any(), any()) }
        }

    private fun makeSocketModeCheckpointManager(): CheckpointManager {
        return CheckpointManager(
            catalog,
            syncManager,
            outputConsumer,
            timeProvider,
            socketMode = true,
            NamespaceMapper(NamespaceDefinitionType.SOURCE),
        )
    }
}
