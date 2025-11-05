/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.GlobalSnapshotCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class StateKeyClientTest {

    @Test
    fun `SelfDescribingStateKeyClient#getPartitionKey should use checkpoint id from message`() {
        // Given
        val client = SelfDescribingStateKeyClient()
        val message = mockk<DestinationRecordRaw>()
        every { message.checkpointId!!.value } returns "namespace-partition-123"

        // When
        val result = client.getPartitionKey(message)

        // Then
        assertEquals(PartitionKey("namespace-partition-123"), result)
    }

    @Test
    fun `SelfDescribingStateKeyClient#getStateKey should use ordinal and partition ids from checkpoint message`() {
        // Given
        val client = SelfDescribingStateKeyClient()
        val message = mockk<CheckpointMessage>()

        every { message.checkpointOrdinalRaw } returns 42
        every { message.checkpointPartitionIds } returns
            listOf("partition-1", "partition-2", "partition-3")

        // When
        val result = client.getStateKey(message)

        // Then
        val expectedPartitions =
            listOf(
                PartitionKey("partition-1"),
                PartitionKey("partition-2"),
                PartitionKey("partition-3")
            )
        assertEquals(StateKey(42L, expectedPartitions), result)
    }

    @Test
    fun `SelfDescribingStateKeyClient#getStateKey should handle empty partition list`() {
        // Given
        val client = SelfDescribingStateKeyClient()
        val message = mockk<CheckpointMessage>()

        every { message.checkpointOrdinalRaw } returns 100
        every { message.checkpointPartitionIds } returns emptyList()

        // When
        val result = client.getStateKey(message)

        // Then
        assertEquals(StateKey(100L, emptyList()), result)
    }

    @Test
    fun `SelfDescribingStateKeyClient#getStateKey should handle single partition`() {
        // Given
        val client = SelfDescribingStateKeyClient()
        val message = mockk<CheckpointMessage>()

        every { message.checkpointOrdinalRaw } returns 5
        every { message.checkpointPartitionIds } returns listOf("single-partition")

        // When
        val result = client.getStateKey(message)

        // Then
        assertEquals(StateKey(5L, listOf(PartitionKey("single-partition"))), result)
    }

    @Test
    fun `InferredStateKeyClient#getPartitionKey should return per-stream partition key`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream, Fixtures.productsStream))
        val client = InferredStateKeyClient(catalog)
        val message1 = mockk<DestinationRecordRaw>()
        val message2 = mockk<DestinationRecordRaw>()

        every { message1.stream } returns Fixtures.usersStream
        every { message2.stream } returns Fixtures.productsStream

        // When
        val result1 = client.getPartitionKey(message1)
        val result2 = client.getPartitionKey(message2)

        // Then
        assertEquals(PartitionKey("namespace-users-1"), result1)
        assertEquals(PartitionKey("products-1"), result2)
    }

    @Test
    fun `InferredStateKeyClient#getStateKey should handle StreamCheckpoint with single partition`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream))
        val client = InferredStateKeyClient(catalog)
        val checkpoint = mockk<CheckpointMessage.Checkpoint>()
        every { checkpoint.unmappedDescriptor } returns Fixtures.usersStream.unmappedDescriptor

        val message1 = mockk<StreamCheckpoint>()
        val message2 = mockk<StreamCheckpoint>()

        every { message1.checkpoint } returns checkpoint
        every { message2.checkpoint } returns checkpoint

        // When
        val result1 = client.getStateKey(message1)
        val result2 = client.getStateKey(message2)

        // Then
        assertEquals(StateKey(1L, listOf(PartitionKey("namespace-users-1"))), result1)
        // second
        assertEquals(StateKey(2L, listOf(PartitionKey("namespace-users-2"))), result2)
    }

    @Test
    fun `InferredStateKeyClient#getStateKey should handle GlobalCheckpoint with all stream partitions`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream, Fixtures.productsStream))
        val client = InferredStateKeyClient(catalog)
        val globalCheckpoint = mockk<GlobalCheckpoint>()

        // When
        val result = client.getStateKey(globalCheckpoint)

        // Then
        assertEquals(
            StateKey(1L, listOf(PartitionKey("namespace-users-1"), PartitionKey("products-1"))),
            result
        )
    }

    @Test
    fun `InferredStateKeyClient#getStateKey should handle GlobalSnapshotCheckpoint with all stream partitions`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream, Fixtures.productsStream))
        val client = InferredStateKeyClient(catalog)
        val globalSnapshotCheckpoint = mockk<GlobalSnapshotCheckpoint>()

        // When
        val result = client.getStateKey(globalSnapshotCheckpoint)

        // Then
        assertEquals(
            StateKey(1L, listOf(PartitionKey("namespace-users-1"), PartitionKey("products-1"))),
            result
        )
    }

    @Test
    fun `InferredStateKeyClient#getPartitionKey should reflect incremented counter after getStateKey`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream))
        val client = InferredStateKeyClient(catalog)
        val recordMessage = mockk<DestinationRecordRaw>()
        val checkpoint = mockk<CheckpointMessage.Checkpoint>()
        val checkpointMessage = mockk<StreamCheckpoint>()

        every { recordMessage.stream } returns Fixtures.usersStream
        every { checkpoint.unmappedDescriptor } returns Fixtures.usersStream.unmappedDescriptor
        every { checkpointMessage.checkpoint } returns checkpoint

        // When
        val partitionKey1 = client.getPartitionKey(recordMessage)
        val stateKey1 = client.getStateKey(checkpointMessage) // This increments stream counter
        val partitionKey2 = client.getPartitionKey(recordMessage)

        // Then
        assertEquals(PartitionKey("namespace-users-1"), partitionKey1) // Initial value
        assertEquals(
            StateKey(1L, listOf(PartitionKey("namespace-users-1"))),
            stateKey1
        ) // Uses counter 1, then increments
        assertEquals(
            PartitionKey("namespace-users-2"),
            partitionKey2
        ) // Current value after increment
    }

    @Test
    fun `InferredStateKeyClient should maintain independent counter per stream`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream, Fixtures.productsStream))
        val client = InferredStateKeyClient(catalog)

        val checkpoint1 = mockk<CheckpointMessage.Checkpoint>()
        val checkpoint2 = mockk<CheckpointMessage.Checkpoint>()
        every { checkpoint1.unmappedDescriptor } returns Fixtures.usersStream.unmappedDescriptor
        every { checkpoint2.unmappedDescriptor } returns Fixtures.productsStream.unmappedDescriptor

        val streamCheckpoint1 = mockk<StreamCheckpoint>()
        val streamCheckpoint2 = mockk<StreamCheckpoint>()
        val streamCheckpoint3 = mockk<StreamCheckpoint>()

        every { streamCheckpoint1.checkpoint } returns checkpoint1
        every { streamCheckpoint2.checkpoint } returns checkpoint2
        every { streamCheckpoint3.checkpoint } returns checkpoint1

        // When
        val result1 = client.getStateKey(streamCheckpoint1) // Fixtures.usersStream, counter 1
        val result2 = client.getStateKey(streamCheckpoint2) // products, counter 1
        val result3 = client.getStateKey(streamCheckpoint3) // Fixtures.usersStream, counter 2

        // Then
        assertEquals(StateKey(1L, listOf(PartitionKey("namespace-users-1"))), result1)
        assertEquals(StateKey(1L, listOf(PartitionKey("products-1"))), result2)
        assertEquals(StateKey(2L, listOf(PartitionKey("namespace-users-2"))), result3)
    }

    @Test
    fun `InferredStateKeyClient global counter should increment for all checkpoint types`() {
        // Given
        val catalog = DestinationCatalog(listOf(Fixtures.usersStream))
        val client = InferredStateKeyClient(catalog)

        val checkpoint = mockk<CheckpointMessage.Checkpoint>()
        every { checkpoint.unmappedDescriptor } returns Fixtures.usersStream.unmappedDescriptor

        val streamCheckpoint = mockk<StreamCheckpoint>()
        val globalCheckpoint = mockk<GlobalCheckpoint>()
        val globalSnapshotCheckpoint = mockk<GlobalSnapshotCheckpoint>()

        every { streamCheckpoint.checkpoint } returns checkpoint

        // When
        val result1 = client.getStateKey(streamCheckpoint)
        val result2 = client.getStateKey(globalCheckpoint)
        val result3 = client.getStateKey(globalSnapshotCheckpoint)

        // Then - Global counter increments for each call
        assertEquals(1L, result1.id)
        assertEquals(2L, result2.id)
        assertEquals(3L, result3.id)
    }

    object Fixtures {

        val usersStream = createStream("namespace", "users")
        val productsStream = createStream(null, "products")

        private fun createStream(namespace: String?, name: String): DestinationStream {
            val descriptor = DestinationStream.Descriptor(namespace, name)
            return mockk<DestinationStream> {
                // actually used by class
                every { unmappedDescriptor } returns descriptor
                // below is just for the catalog initialization
                every { mappedDescriptor } returns descriptor
                every { importType } returns Append
            }
        }
    }
}
