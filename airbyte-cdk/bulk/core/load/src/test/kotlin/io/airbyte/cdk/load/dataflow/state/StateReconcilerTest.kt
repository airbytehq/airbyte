/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
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
import kotlin.time.toJavaDuration
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
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

    @MockK private lateinit var emittedStatsStore: EmittedStatsStore

    private val interval = 30.seconds

    private lateinit var testScope: TestScope

    private lateinit var reconcilerScope: CoroutineScope

    private lateinit var stateReconciler: StateReconciler

    @BeforeEach
    fun setUp() {
        testScope = TestScope(StandardTestDispatcher())
        reconcilerScope = CoroutineScope(testScope.coroutineContext)

        stateReconciler =
            StateReconciler(
                stateStore,
                emittedStatsStore,
                consumer,
                reconcilerScope,
                interval.toJavaDuration(),
            )
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
    fun `publish should send the protocol message to the ouput consumer`() {
        // Given
        val protocolMessage = mockk<AirbyteMessage>()

        every { consumer.accept(protocolMessage) } just Runs

        // When
        stateReconciler.publish(protocolMessage)

        // Then
        verify { consumer.accept(protocolMessage) }
    }

    @Test
    fun `run should flush at the defined interval`() = runTest {
        // Given
        val checkpointMessage1 = mockk<CheckpointMessage>()
        val checkpointMessage2 = mockk<CheckpointMessage>()
        val stateMessage1 = mockk<AirbyteMessage>()
        val stateMessage2 = mockk<AirbyteMessage>()
        every { checkpointMessage1.asProtocolMessage() } returns stateMessage1
        every { checkpointMessage2.asProtocolMessage() } returns stateMessage2

        every { stateStore.getNextComplete() } returnsMany
            listOf(
                // first flush
                checkpointMessage1,
                checkpointMessage2,
                null,
                // second flush
                checkpointMessage2,
                null,
                // third flush
                checkpointMessage1,
                null,
            )

        val statsMessage1 = mockk<AirbyteMessage>()
        val statsMessage2 = mockk<AirbyteMessage>()
        val statsList = listOf(statsMessage1, statsMessage2)
        every { emittedStatsStore.getStats() } returns statsList

        every { consumer.accept(any<AirbyteMessage>()) } just Runs

        // Create a new reconciler with the test scope for this test
        val localReconciler =
            StateReconciler(
                stateStore,
                emittedStatsStore,
                consumer,
                this.backgroundScope,
                interval.toJavaDuration(),
            )

        // When
        localReconciler.run()

        // Advance time to trigger multiple flushes
        advanceTimeBy(interval) // First flush
        advanceTimeBy(1.seconds) // Padding
        // Then
        verify(exactly = 1) { consumer.accept(stateMessage1) }
        verify(exactly = 1) { consumer.accept(stateMessage2) }
        verify(exactly = 1) { consumer.accept(statsMessage1) }
        verify(exactly = 1) { consumer.accept(statsMessage2) }

        advanceTimeBy(interval) // Second flush
        advanceTimeBy(1.seconds) // Padding
        // Then
        verify(exactly = 2) { consumer.accept(stateMessage2) }
        verify(exactly = 2) { consumer.accept(statsMessage1) }
        verify(exactly = 2) { consumer.accept(statsMessage2) }

        advanceTimeBy(30.seconds) // Third flush
        advanceTimeBy(1.seconds) // Padding
        // Then
        verify(exactly = 2) { consumer.accept(stateMessage1) }
        verify(exactly = 3) { consumer.accept(statsMessage1) }
        verify(exactly = 3) { consumer.accept(statsMessage2) }
    }

    @Test
    fun `disable should cancel the job and no more flushes should occur`() = runTest {
        // Given
        every { stateStore.getNextComplete() } returns null
        every { emittedStatsStore.getStats() } returns null

        // Create a new reconciler with the test scope for this test
        val localReconciler =
            StateReconciler(
                stateStore,
                emittedStatsStore,
                consumer,
                this.backgroundScope,
                interval.toJavaDuration(),
            )

        // Start the reconciler
        localReconciler.run()

        // When
        localReconciler.disable()

        // Then
        advanceTimeBy(60.seconds)

        // Should have had initial flushes but then stopped after disable
        verify(exactly = 0) { stateStore.getNextComplete() }
        verify(exactly = 0) { emittedStatsStore.getStats() }
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
    fun `flushEmittedStats should publish all stats from emittedStatsStore`() {
        // Given
        val statsMessage1 = mockk<AirbyteMessage>()
        val statsMessage2 = mockk<AirbyteMessage>()
        val statsMessage3 = mockk<AirbyteMessage>()
        val statsList = listOf(statsMessage1, statsMessage2, statsMessage3)

        every { emittedStatsStore.getStats() } returns statsList
        every { consumer.accept(any<AirbyteMessage>()) } just Runs

        // When
        stateReconciler.flushEmittedStats()

        // Then
        verify(exactly = 1) { emittedStatsStore.getStats() }
        verify { consumer.accept(statsMessage1) }
        verify { consumer.accept(statsMessage2) }
        verify { consumer.accept(statsMessage3) }
    }

    @Test
    fun `flushEmittedStats should handle null stats from store`() {
        // Given
        every { emittedStatsStore.getStats() } returns null

        // When
        stateReconciler.flushEmittedStats()

        // Then
        verify(exactly = 1) { emittedStatsStore.getStats() }
        verify(exactly = 0) { consumer.accept(any<AirbyteMessage>()) }
    }
}
