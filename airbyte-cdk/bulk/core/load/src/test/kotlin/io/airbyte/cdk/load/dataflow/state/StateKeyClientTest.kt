/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
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
        every { message.checkpointId!!.value } returns "test-partition-123"

        // When
        val result = client.getPartitionKey(message)

        // Then
        assertEquals(PartitionKey("test-partition-123"), result)
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
    fun `InferredStateKeyClient#getPartitionKey should return sequential counter as string`() {
        // Given
        val client = InferredStateKeyClient()
        val message1 = mockk<DestinationRecordRaw>()
        val message2 = mockk<DestinationRecordRaw>()

        // When
        val result1 = client.getPartitionKey(message1)
        val result2 = client.getPartitionKey(message2)

        // Then
        assertEquals(PartitionKey("1"), result1)
        assertEquals(PartitionKey("1"), result2) // Should not increment for getPartitionKey
    }

    @Test
    fun `InferredStateKeyClient#getStateKey should increment counter and create single partition`() {
        // Given
        val client = InferredStateKeyClient()
        val message1 = mockk<CheckpointMessage>()
        val message2 = mockk<CheckpointMessage>()
        val message3 = mockk<CheckpointMessage>()

        // When
        val result1 = client.getStateKey(message1)
        val result2 = client.getStateKey(message2)
        val result3 = client.getStateKey(message3)

        // Then
        assertEquals(StateKey(1L, listOf(PartitionKey("1"))), result1)
        assertEquals(StateKey(2L, listOf(PartitionKey("2"))), result2)
        assertEquals(StateKey(3L, listOf(PartitionKey("3"))), result3)
    }

    @Test
    fun `InferredStateKeyClient#getPartitionKey should use current counter value without incrementing`() {
        // Given
        val client = InferredStateKeyClient()
        val recordMessage = mockk<DestinationRecordRaw>()
        val checkpointMessage = mockk<CheckpointMessage>()

        // When
        val partitionKey1 = client.getPartitionKey(recordMessage)
        val stateKey1 = client.getStateKey(checkpointMessage) // This increments
        val partitionKey2 = client.getPartitionKey(recordMessage)

        // Then
        assertEquals(PartitionKey("1"), partitionKey1) // Initial value
        assertEquals(
            StateKey(1L, listOf(PartitionKey("1"))),
            stateKey1
        ) // Incremented to 2 internally
        assertEquals(PartitionKey("2"), partitionKey2) // Current value after increment
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
}
