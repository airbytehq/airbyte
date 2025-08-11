/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.util.concurrent.ConcurrentSkipListMap
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class StateReconcilerTest {
    private val stateWatermarkStore: StateWatermarkStore = mockk(relaxed = true)

    private val stateStore: StateStore = mockk(relaxed = true)

    private val statePublisher: StatePublisher = mockk(relaxed = true)

    private lateinit var stateReconciler: StateReconciler

    @BeforeEach
    fun setup() {
        stateReconciler = StateReconciler(stateWatermarkStore, stateStore, statePublisher)
    }

    @Test
    fun `test flush complete states`() {
        // Given
        val states = mockk<ConcurrentSkipListMap<StateKey, CheckpointMessage>>()
        val key1 = StateKey(1, listOf("1"))
        val key2 = StateKey(2, listOf("2"))
        val key3 = StateKey(3, listOf("3"))
        every { states.firstKey() } returns key1 andThen key2 andThen key3
        every { states.isEmpty() } returns false

        val message1 = mockk<CheckpointMessage>()
        val message2 = mockk<CheckpointMessage>()
        val message3 = mockk<CheckpointMessage>()

        every { stateStore.states } returns states
        every { stateStore.remove(key1) } returns message1
        every { stateStore.remove(key2) } returns message2
        every { stateWatermarkStore.isComplete(key1) } returns true
        every { stateWatermarkStore.isComplete(key2) } returns true
        every { stateWatermarkStore.isComplete(key3) } returns false

        // When
        stateReconciler.flushCompleteStates()

        // Then
        verify(exactly = 1) { statePublisher.publish(message1) }
        verify(exactly = 1) { statePublisher.publish(message2) }
        verify(exactly = 0) { statePublisher.publish(message3) }
        verify(exactly = 1) { stateStore.remove(key1) }
        verify(exactly = 1) { stateStore.remove(key2) }
        verify(exactly = 0) { stateStore.remove(key3) }
    }
}
