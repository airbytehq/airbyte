/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class StateStoreTest {

    @MockK private lateinit var keyClient: StateKeyClient

    @MockK private lateinit var histogramStore: StateHistogramStore

    private lateinit var stateStore: StateStore

    @BeforeEach
    fun setUp() {
        stateStore = StateStore(keyClient, histogramStore)
        every { histogramStore.remove(any()) } returns 1L
    }

    @Test
    fun `accept should store checkpoint message and update histogram`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(stateKey, 100L) } returns mockk()

        // When
        stateStore.accept(checkpointMessage)

        // Then
        verify { keyClient.getStateKey(checkpointMessage) }
        verify { histogramStore.acceptExpectedCounts(stateKey, 100L) }
    }

    @Test
    fun `remove should return and remove the checkpoint message for given key`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()

        stateStore.accept(checkpointMessage)

        // When
        val removedMessage = stateStore.remove(stateKey)

        // Then
        assertEquals(checkpointMessage, removedMessage)
    }

    @Test
    fun `getNextComplete should return null when no states exist`() {
        // When
        val result = stateStore.getNextComplete()

        // Then
        assertNull(result)
    }

    @Test
    fun `getNextComplete should return null when first state id does not match sequence`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(5L, listOf(PartitionKey("partition-1"))) // Not sequence 1

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()

        stateStore.accept(checkpointMessage)

        // When
        val result = stateStore.getNextComplete()

        // Then
        assertNull(result)
    }

    @Test
    fun `getNextComplete should return null when state is not complete`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(stateKey) } returns false

        stateStore.accept(checkpointMessage)

        // When
        val result = stateStore.getNextComplete()

        // Then
        assertNull(result)
        verify { histogramStore.isComplete(stateKey) }
    }

    @Test
    fun `getNextComplete should return and remove state when it matches sequence and is complete`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(stateKey) } returns true

        stateStore.accept(checkpointMessage)

        // When
        val result = stateStore.getNextComplete()

        // Then
        assertEquals(checkpointMessage, result)
        verify { histogramStore.isComplete(stateKey) }

        // Verify state was removed
        val secondResult = stateStore.getNextComplete()
        assertNull(secondResult)
    }

    @Test
    fun `getNextComplete should process states in sequence order`() {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>(relaxed = true)
        val checkpointMessage2 = mockk<CheckpointMessage>(relaxed = true)
        val checkpointMessage3 = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()

        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))
        val stateKey3 = StateKey(3L, listOf(PartitionKey("partition-3")))

        every { checkpointMessage1.sourceStats } returns sourceStats
        every { checkpointMessage2.sourceStats } returns sourceStats
        every { checkpointMessage3.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L

        every { keyClient.getStateKey(checkpointMessage1) } returns stateKey1
        every { keyClient.getStateKey(checkpointMessage2) } returns stateKey2
        every { keyClient.getStateKey(checkpointMessage3) } returns stateKey3
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(any()) } returns true

        // Add in reverse order
        stateStore.accept(checkpointMessage3)
        stateStore.accept(checkpointMessage1)
        stateStore.accept(checkpointMessage2)

        // When & Then
        assertEquals(checkpointMessage1, stateStore.getNextComplete()) // sequence 1
        assertEquals(checkpointMessage2, stateStore.getNextComplete()) // sequence 2
        assertEquals(checkpointMessage3, stateStore.getNextComplete()) // sequence 3
        assertNull(stateStore.getNextComplete()) // no more states
    }

    @Test
    fun `getNextComplete should skip incomplete states and not advance sequence`() {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>(relaxed = true)
        val checkpointMessage2 = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()

        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))

        every { checkpointMessage1.sourceStats } returns sourceStats
        every { checkpointMessage2.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L

        every { keyClient.getStateKey(checkpointMessage1) } returns stateKey1
        every { keyClient.getStateKey(checkpointMessage2) } returns stateKey2
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(stateKey1) } returns false // incomplete
        every { histogramStore.isComplete(stateKey2) } returns true

        stateStore.accept(checkpointMessage1)
        stateStore.accept(checkpointMessage2)

        // When
        val result1 = stateStore.getNextComplete() // should be null because state 1 is incomplete

        // Make state 1 complete now
        every { histogramStore.isComplete(stateKey1) } returns true
        val result2 = stateStore.getNextComplete() // should return state 1

        // Then
        assertNull(result1)
        assertEquals(checkpointMessage1, result2)
    }

    @Test
    fun `hasStates should return false when store is empty`() {
        // When
        val result = stateStore.hasStates()

        // Then
        assertFalse(result)
    }

    @Test
    fun `hasStates should return true when states are present`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()

        // When
        stateStore.accept(checkpointMessage)
        val result = stateStore.hasStates()

        // Then
        assertTrue(result)
    }

    @Test
    fun `hasStates should return false after all states are removed`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()
        val stateKey = StateKey(1L, listOf(PartitionKey("partition-1")))

        every { checkpointMessage.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L
        every { keyClient.getStateKey(checkpointMessage) } returns stateKey
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(stateKey) } returns true

        // Add a state
        stateStore.accept(checkpointMessage)
        assertTrue(stateStore.hasStates())

        // Remove the state via getNextComplete
        stateStore.getNextComplete()

        // Then
        assertFalse(stateStore.hasStates())
    }

    @Test
    fun `hasStates should return true when multiple states exist`() {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>(relaxed = true)
        val checkpointMessage2 = mockk<CheckpointMessage>(relaxed = true)
        val sourceStats = mockk<CheckpointMessage.Stats>()

        val stateKey1 = StateKey(1L, listOf(PartitionKey("partition-1")))
        val stateKey2 = StateKey(2L, listOf(PartitionKey("partition-2")))

        every { checkpointMessage1.sourceStats } returns sourceStats
        every { checkpointMessage2.sourceStats } returns sourceStats
        every { sourceStats.recordCount } returns 100L

        every { keyClient.getStateKey(checkpointMessage1) } returns stateKey1
        every { keyClient.getStateKey(checkpointMessage2) } returns stateKey2
        every { histogramStore.acceptExpectedCounts(any(), any()) } returns mockk()
        every { histogramStore.isComplete(stateKey1) } returns true

        // Add multiple states
        stateStore.accept(checkpointMessage1)
        stateStore.accept(checkpointMessage2)

        // Then
        assertTrue(stateStore.hasStates())

        // Remove one state
        stateStore.getNextComplete()

        // Should still have states
        assertTrue(stateStore.hasStates())
    }
}
