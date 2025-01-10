/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class CheckpointManagerUTest {
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) lateinit var syncManager: SyncManager
    private val outputConsumer: suspend (Reserved<CheckpointMessage>) -> Unit =
        mockk<suspend (Reserved<CheckpointMessage>) -> Unit>(relaxed = true)
    @MockK(relaxed = true) lateinit var timeProvider: TimeProvider

    @Test
    fun `test checkpoint manager does not ignore ready checkpoint after empty one`() = runTest {
        // Populate the mock catalog with two streams in order
        val stream1 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream1"),
                importType = Append,
                schema = ObjectTypeWithEmptySchema,
                generationId = 10L,
                minimumGenerationId = 10L,
                syncId = 101L
            )
        val stream2 =
            DestinationStream(
                DestinationStream.Descriptor("test", "stream2"),
                importType = Append,
                schema = ObjectTypeWithEmptySchema,
                generationId = 10L,
                minimumGenerationId = 10L,
                syncId = 101L
            )

        coEvery { catalog.streams } returns listOf(stream1, stream2)

        val checkpointManager =
            DefaultCheckpointManager(catalog, syncManager, outputConsumer, timeProvider)

        // Add a checkpoint for only the second stream
        val message = mockk<Reserved<CheckpointMessage>>(relaxed = true)
        checkpointManager.addStreamCheckpoint(stream2.descriptor, 1, message)

        // Ensure second stream is data sufficient
        val stream2Manager = mockk<StreamManager>(relaxed = true)
        coEvery { stream2Manager.areRecordsPersistedUntil(any()) } returns true
        coEvery { syncManager.getStreamManager(stream2.descriptor) } returns stream2Manager

        // Ensure { first stream is empty } doesn't block sending the second stream
        coEvery { outputConsumer.invoke(any()) } returns Unit
        checkpointManager.flushReadyCheckpointMessages()
        coVerify { outputConsumer.invoke(message) }
    }
}
