/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class CheckpointManagerUTest {
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) lateinit var syncManager: SyncManager
    private val outputConsumer: suspend (Reserved<CheckpointMessage>, Long, Long) -> Unit =
        mockk<suspend (Reserved<CheckpointMessage>, Long, Long) -> Unit>(relaxed = true)
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
        coEvery { outputConsumer.invoke(any(), any(), any()) } returns Unit
        coEvery { syncManager.getStreamManager(stream1.descriptor) } returns streamManager1
        coEvery { syncManager.getStreamManager(stream2.descriptor) } returns streamManager2
    }

    private fun makeCheckpointManager(): CheckpointManager<Reserved<CheckpointMessage>> {
        return CheckpointManager(catalog, syncManager, outputConsumer, timeProvider)
    }

    private fun makeKey(index: Int, id: String? = null) =
        CheckpointKey(
            checkpointIndex = CheckpointIndex(index),
            checkpointId = CheckpointId(id ?: index.toString())
        )

    @Test
    fun `test checkpoint-by-id`() = runTest {
        val checkpointManager = makeCheckpointManager()

        val message1 = mockk<Reserved<CheckpointMessage>>(relaxed = true)
        val message2 = mockk<Reserved<CheckpointMessage>>(relaxed = true)

        checkpointManager.addStreamCheckpoint(stream1.descriptor, makeKey(1), message1)
        checkpointManager.addStreamCheckpoint(stream2.descriptor, makeKey(1), message2)

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("1")) } returns false
        coEvery { streamManager2.areRecordsPersistedForCheckpoint(CheckpointId("1")) } returns true

        // Only stream2 should be flushed.
        checkpointManager.flushReadyCheckpointMessages()
        coVerify(exactly = 0) { outputConsumer.invoke(message1, any(), any()) }
        coVerify(exactly = 1) { outputConsumer.invoke(message2, any(), any()) }
    }

    @Test
    fun `checkpoint N will not be emitted before N-1`() = runTest {
        val checkpointManager = makeCheckpointManager()

        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(1, "one"),
            mockk(relaxed = true)
        )
        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(2, "two"),
            mockk(relaxed = true)
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            false
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            true

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 0) { outputConsumer.invoke(any(), any(), any()) }
    }

    @Test
    fun `checkpoint N will be emitted after N-1`() = runTest {
        val checkpointManager = makeCheckpointManager()

        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(1, "one"),
            mockk(relaxed = true)
        )
        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(2, "two"),
            mockk(relaxed = true)
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            true
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            true

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 2) { outputConsumer.invoke(any(), any(), any()) }
    }

    @Test
    fun `checkpoints will be emitted in order even if received out of order`() = runTest {
        val checkpointManager = makeCheckpointManager()

        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(2, "two"),
            mockk(relaxed = true)
        )
        checkpointManager.addStreamCheckpoint(
            stream1.descriptor,
            makeKey(1, "one"),
            mockk(relaxed = true)
        )

        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("one")) } returns
            true
        coEvery { streamManager1.areRecordsPersistedForCheckpoint(CheckpointId("two")) } returns
            false

        checkpointManager.flushReadyCheckpointMessages()

        coVerify(exactly = 1) { outputConsumer.invoke(any(), any(), any()) }
    }
}
