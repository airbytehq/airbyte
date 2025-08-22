/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.Undefined
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class DataFlowPipelineInputFlowTest {
    @Test
    fun `checkpoint message`() = runBlocking {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val inputFlow = flowOf<DestinationMessage>(checkpointMessage)
        val stateStore = mockk<StateStore>(relaxed = true)
        val stateKeyClient = mockk<StateKeyClient>()
        val completionTracker = mockk<StreamCompletionTracker>()
        val dataFlowPipelineInputFlow =
            DataFlowPipelineInputFlow(inputFlow, stateStore, stateKeyClient, completionTracker)

        // When
        val result = dataFlowPipelineInputFlow.toList()

        // Then
        coVerify(exactly = 1) { stateStore.accept(checkpointMessage) }
        assertEquals(0, result.size)
    }

    @Test
    fun `destination record`() = runBlocking {
        // Given
        val stream = mockk<DestinationStream>()
        every { stream.schema } returns mockk()
        every { stream.airbyteValueProxyFieldAccessors } returns emptyArray()
        val message = mockk<DestinationRecordSource>()
        every { message.fileReference } returns null
        val destinationRecord =
            DestinationRecord(
                stream,
                message,
                1L,
                null,
                UUID.randomUUID(),
            )
        val inputFlow = flowOf<DestinationMessage>(destinationRecord)
        val stateStore = mockk<StateStore>()
        val stateKeyClient = mockk<StateKeyClient>()
        val completionTracker = mockk<StreamCompletionTracker>()
        val partitionKey = PartitionKey("partitionKey")
        every { stateKeyClient.getPartitionKey(any()) } returns partitionKey
        val dataFlowPipelineInputFlow =
            DataFlowPipelineInputFlow(inputFlow, stateStore, stateKeyClient, completionTracker)

        // When
        val result = dataFlowPipelineInputFlow.toList()

        // Then
        assertEquals(1, result.size)
        val expected =
            DataFlowStageIO(
                raw = destinationRecord.asDestinationRecordRaw(),
                partitionKey = partitionKey,
            )
        assertEquals(expected, result[0])
    }

    @Test
    fun `stream complete`() = runBlocking {
        // Given
        val stream = mockk<DestinationStream>()
        every { stream.schema } returns mockk()
        every { stream.airbyteValueProxyFieldAccessors } returns emptyArray()
        val message = mockk<DestinationRecordSource>()
        every { message.fileReference } returns null
        val streamComplete =
            DestinationRecordStreamComplete(
                stream,
                1L,
            )
        val inputFlow = flowOf<DestinationMessage>(streamComplete)
        val stateStore = mockk<StateStore>()
        val stateKeyClient = mockk<StateKeyClient>()
        val completionTracker = mockk<StreamCompletionTracker>(relaxed = true)
        val partitionKey = PartitionKey("partitionKey")
        every { stateKeyClient.getPartitionKey(any()) } returns partitionKey
        val dataFlowPipelineInputFlow =
            DataFlowPipelineInputFlow(inputFlow, stateStore, stateKeyClient, completionTracker)

        // When
        val result = dataFlowPipelineInputFlow.toList()

        // Then
        coVerify(exactly = 1) { completionTracker.accept(streamComplete) }
        assertEquals(0, result.size)
    }

    @Test
    fun `other message`() = runBlocking {
        // Given
        val undefinedMessage = Undefined
        val inputFlow = flowOf<DestinationMessage>(undefinedMessage)
        val stateStore = mockk<StateStore>()
        val stateKeyClient = mockk<StateKeyClient>()
        val completionTracker = mockk<StreamCompletionTracker>()
        val dataFlowPipelineInputFlow =
            DataFlowPipelineInputFlow(inputFlow, stateStore, stateKeyClient, completionTracker)

        // When
        val result = dataFlowPipelineInputFlow.toList()

        // Then
        assertEquals(0, result.size)
    }
}
