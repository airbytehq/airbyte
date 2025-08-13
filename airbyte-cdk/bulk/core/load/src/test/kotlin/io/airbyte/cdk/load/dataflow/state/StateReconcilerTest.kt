/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.Runs
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import io.mockk.verifyOrder
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
@OptIn(ExperimentalCoroutinesApi::class)
class StateReconcilerTest {

    @MockK private lateinit var stateStore: StateStore

    @MockK private lateinit var consumer: OutputConsumer

    private lateinit var stateReconciler: StateReconciler

    @BeforeEach
    fun setUp() {
        stateReconciler = StateReconciler(stateStore, consumer)
    }

    @Test
    fun `flushCompleteStates should publish all complete states from store`() {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>()
        val checkpointMessage2 = mockk<CheckpointMessage>()
        val checkpointMessage3 = mockk<CheckpointMessage>()
        val protocolMessage1 = mockk<AirbyteMessage>()
        val protocolMessage2 = mockk<AirbyteMessage>()
        val protocolMessage3 = mockk<AirbyteMessage>()

        every { checkpointMessage1.asProtocolMessage() } returns protocolMessage1
        every { checkpointMessage2.asProtocolMessage() } returns protocolMessage2
        every { checkpointMessage3.asProtocolMessage() } returns protocolMessage3
        every { consumer.accept(any<AirbyteMessage>()) } just Runs

        every { stateStore.getNextComplete() } returnsMany
            listOf(checkpointMessage1, checkpointMessage2, checkpointMessage3, null)

        // When
        stateReconciler.flushCompleteStates()

        // Then
        verify(exactly = 4) { stateStore.getNextComplete() }
        verify { consumer.accept(protocolMessage1) }
        verify { consumer.accept(protocolMessage2) }
        verify { consumer.accept(protocolMessage3) }
    }

    @Test
    fun `flushCompleteStates should handle empty state store`() {
        // Given
        every { stateStore.getNextComplete() } returns null

        // When
        stateReconciler.flushCompleteStates()

        // Then
        verify(exactly = 1) { stateStore.getNextComplete() }
        verify(exactly = 0) { consumer.accept(any<AirbyteMessage>()) }
    }

    @Test
    fun `publish should convert checkpoint message to protocol message and send to consumer`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val protocolMessage = mockk<AirbyteMessage>()

        every { checkpointMessage.asProtocolMessage() } returns protocolMessage
        every { consumer.accept(protocolMessage) } just Runs

        // When
        stateReconciler.publish(checkpointMessage)

        // Then
        verify { checkpointMessage.asProtocolMessage() }
        verify { consumer.accept(protocolMessage) }
    }

    @Test
    fun `run should continue flushing states at regular intervals`() = runTest {
        // Given
        every { stateStore.getNextComplete() } returns null

        // When
        stateReconciler.run(this.backgroundScope)

        // Advance time to trigger multiple flushes
        advanceTimeBy(30.seconds) // First flush
        advanceTimeBy(30.seconds) // Second flush
        advanceTimeBy(30.seconds) // Third flush
        advanceTimeBy(1.seconds) // Padding to let the last flush run

        // Then
        verify(atLeast = 3) { stateStore.getNextComplete() }
    }

    @Test
    fun `disable should cancel the job and no more flushes should occur`() = runTest {
        // Given
        every { stateStore.getNextComplete() } returns null

        // Start the reconciler
        stateReconciler.run(this.backgroundScope)

        // When
        stateReconciler.disable()

        // Then
        advanceTimeBy(60.seconds)

        // Should have had initial flushes but then stopped after disable
        verify(exactly = 0) { stateStore.getNextComplete() }
    }

    @Test
    fun `flushCompleteStates should process states in correct order`() {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>()
        val checkpointMessage2 = mockk<CheckpointMessage>()
        val protocolMessage1 = mockk<AirbyteMessage>()
        val protocolMessage2 = mockk<AirbyteMessage>()

        every { checkpointMessage1.asProtocolMessage() } returns protocolMessage1
        every { checkpointMessage2.asProtocolMessage() } returns protocolMessage2
        every { consumer.accept(any<AirbyteMessage>()) } just Runs

        every { stateStore.getNextComplete() } returnsMany
            listOf(checkpointMessage1, checkpointMessage2, null)

        // When
        stateReconciler.flushCompleteStates()

        // Then
        verifyOrder {
            stateStore.getNextComplete() // Gets first message
            consumer.accept(protocolMessage1) // Publishes first message
            stateStore.getNextComplete() // Gets second message
            consumer.accept(protocolMessage2) // Publishes second message
            stateStore.getNextComplete() // Gets null, ends loop
        }
    }

    @Test
    fun `publish should handle exception from consumer gracefully`() {
        // Given
        val checkpointMessage = mockk<CheckpointMessage>()
        val protocolMessage = mockk<AirbyteMessage>()

        every { checkpointMessage.asProtocolMessage() } returns protocolMessage
        every { consumer.accept(protocolMessage) } throws RuntimeException("Consumer error")

        // When & Then
        try {
            stateReconciler.publish(checkpointMessage)
        } catch (e: RuntimeException) {
            // Expected - let the exception propagate
            assert(e.message == "Consumer error")
        }

        verify { checkpointMessage.asProtocolMessage() }
        verify { consumer.accept(protocolMessage) }
    }

    @Test
    fun `flushCompleteStates should handle exception from state store gracefully`() {
        // Given
        every { stateStore.getNextComplete() } throws RuntimeException("StateStore error")

        // When & Then
        try {
            stateReconciler.flushCompleteStates()
        } catch (e: RuntimeException) {
            // Expected - let the exception propagate
            assert(e.message == "StateStore error")
        }

        verify { stateStore.getNextComplete() }
        verify(exactly = 0) { consumer.accept(any<AirbyteMessage>()) }
    }
}
