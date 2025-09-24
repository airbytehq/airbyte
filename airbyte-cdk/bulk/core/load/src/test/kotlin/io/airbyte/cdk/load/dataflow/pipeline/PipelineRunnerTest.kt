/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.config.ConnectorInputStreams
import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifySequence
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import kotlin.coroutines.CoroutineContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExecutorCoroutineDispatcher
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class PipelineRunnerTest {

    @MockK(relaxed = true) private lateinit var reconciler: StateReconciler
    @MockK(relaxed = true) private lateinit var aggregateDispatcher: ExecutorCoroutineDispatcher

    @MockK(relaxed = true) private lateinit var store: StateStore

    @MockK private lateinit var pipeline1: DataFlowPipeline

    @MockK private lateinit var pipeline2: DataFlowPipeline

    @MockK private lateinit var pipeline3: DataFlowPipeline

    @MockK(relaxed = true) private lateinit var inputStreams: ConnectorInputStreams

    @BeforeEach
    fun setup() {
        every { store.hasStates() } returns false
    }

    @Test
    fun `run should execute all pipelines concurrently`() = runTest {
        // Given
        val pipelineScope = Fixtures.testScope(this.coroutineContext)
        val runner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1, pipeline2, pipeline3),
                inputStreams,
                pipelineScope,
                aggregateDispatcher
            )

        coEvery { pipeline1.run() } coAnswers { delay(100) }
        coEvery { pipeline2.run() } coAnswers { delay(50) }
        coEvery { pipeline3.run() } coAnswers { delay(75) }

        // When
        runner.run()
        testScheduler.advanceUntilIdle()

        // Then
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { pipeline2.run() }
        coVerify(exactly = 1) { pipeline3.run() }

        coVerify(exactly = 1) { reconciler.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
    }

    @Test
    fun `run should disable reconciler even when pipeline fails`() = runTest {
        // Given
        val exception = RuntimeException("Pipeline failed")
        coEvery { pipeline1.run() } throws exception
        val failingScope = Fixtures.testScope(this.coroutineContext)
        val failingRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                failingScope,
                aggregateDispatcher
            )

        // When/Then
        val thrownException =
            assertThrows<RuntimeException> {
                failingRunner.run()
                testScheduler.advanceUntilIdle()
            }

        assertEquals("Pipeline failed", thrownException.message)

        // Verify reconciler was still disabled
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should execute operations in correct order`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
        val singlePipelineRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                singlePipelineScope,
                aggregateDispatcher
            )

        // When
        singlePipelineRunner.run()
        testScheduler.advanceUntilIdle()

        // Then - verify order of operations
        coVerifySequence {
            reconciler.run()
            pipeline1.run()
            reconciler.disable()
            aggregateDispatcher.close()
            reconciler.flushCompleteStates()
        }
    }

    @Test
    fun `run should start reconciler without parameters`() = runTest {
        // Given
        val emptyScope = Fixtures.testScope(this.coroutineContext)
        val emptyRunner =
            PipelineRunner(
                reconciler,
                store,
                emptyList(),
                inputStreams,
                emptyScope,
                aggregateDispatcher
            )

        // When
        emptyRunner.run()

        // Then
        coVerify(exactly = 1) { reconciler.run() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
    }

    @Test
    fun `run should handle single pipeline`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
        val singlePipelineRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                singlePipelineScope,
                aggregateDispatcher
            )

        // When
        singlePipelineRunner.run()
        testScheduler.advanceUntilIdle()

        // Then
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.run() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should handle reconciler disable failure`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        coEvery { reconciler.disable() } throws RuntimeException("Failed to disable")
        val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
        val singlePipelineRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                singlePipelineScope,
                aggregateDispatcher
            )

        // When/Then
        val exception =
            assertThrows<RuntimeException> {
                singlePipelineRunner.run()
                testScheduler.advanceUntilIdle()
            }

        assertEquals("Failed to disable", exception.message)

        // Verify pipeline was executed before the failure
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should handle reconciler flushCompleteStates failure`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        every { reconciler.flushCompleteStates() } throws RuntimeException("Failed to flush")
        val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
        val singlePipelineRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                singlePipelineScope,
                aggregateDispatcher
            )

        // When/Then
        val exception =
            assertThrows<RuntimeException> {
                singlePipelineRunner.run()
                testScheduler.advanceUntilIdle()
            }

        assertEquals("Failed to flush", exception.message)

        // Verify everything up to flush was executed
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should close input streams when pipeline fails`() = runTest {
        // Given
        val exception = RuntimeException("Pipeline failed")
        coEvery { pipeline1.run() } throws exception

        val failingScope = Fixtures.testScope(this.coroutineContext)
        val failingRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                failingScope,
                aggregateDispatcher
            )

        // When
        assertThrows<RuntimeException> {
            failingRunner.run()
            testScheduler.advanceUntilIdle()
        }

        // Then - verify that closeAll was called due to exception handler
        verify(atLeast = 1) { inputStreams.closeAll() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
    }

    @Test
    fun `run should handle large number of pipelines`() = runTest {
        // Given
        val pipelines =
            (1..32).map {
                val pipeline = mockk<DataFlowPipeline>()
                coEvery { pipeline.run() } just Runs
                pipeline
            }

        val largeScope = Fixtures.testScope(this.coroutineContext)
        val largeRunner =
            PipelineRunner(
                reconciler,
                store,
                pipelines,
                inputStreams,
                largeScope,
                aggregateDispatcher
            )

        // When
        largeRunner.run()
        testScheduler.advanceUntilIdle()

        // Then
        pipelines.forEach { pipeline -> coVerify(exactly = 1) { pipeline.run() } }
        coVerify(exactly = 1) { reconciler.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { aggregateDispatcher.close() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should wait for all pipelines to complete before disabling reconciler`() = runTest {
        // Given
        var pipeline1Complete = false
        var pipeline2Complete = false
        var reconcilerDisabled = false

        coEvery { pipeline1.run() } coAnswers
            {
                delay(100)
                pipeline1Complete = true
            }
        coEvery { pipeline2.run() } coAnswers
            {
                delay(50)
                pipeline2Complete = true
            }
        coEvery { reconciler.disable() } answers
            {
                reconcilerDisabled = true
                assertTrue(
                    pipeline1Complete,
                    "Pipeline 1 should be complete before disabling reconciler"
                )
                assertTrue(
                    pipeline2Complete,
                    "Pipeline 2 should be complete before disabling reconciler"
                )
            }

        val twoScope = Fixtures.testScope(this.coroutineContext)
        val twoRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1, pipeline2),
                inputStreams,
                twoScope,
                aggregateDispatcher
            )

        // When
        twoRunner.run()
        testScheduler.advanceUntilIdle()

        // Then
        assertTrue(reconcilerDisabled, "Reconciler should have been disabled")
    }

    @Test
    fun `run should throw IllegalStateException when unflushed states exist at sync end`() =
        runTest {
            // Given
            coEvery { pipeline1.run() } just Runs
            every { store.hasStates() } returns true // Simulate unflushed states exist

            val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
            val singlePipelineRunner =
                PipelineRunner(
                    reconciler,
                    store,
                    listOf(pipeline1),
                    inputStreams,
                    singlePipelineScope,
                    aggregateDispatcher
                )

            // When/Then
            val exception =
                assertThrows<IllegalStateException> {
                    singlePipelineRunner.run()
                    testScheduler.advanceUntilIdle()
                }

            // Then
            assertEquals("Sync completed, but unflushed states were detected.", exception.message)

            // Verify all operations completed before the check
            coVerify(exactly = 1) { reconciler.run() }
            coVerify(exactly = 1) { pipeline1.run() }
            coVerify(exactly = 1) { reconciler.disable() }
            coVerify(exactly = 1) { reconciler.flushCompleteStates() }
            coVerify(exactly = 1) { store.hasStates() }
        }

    @Test
    fun `run should not throw exception when all states are flushed`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        every { store.hasStates() } returns false // All states are flushed

        val singlePipelineScope = Fixtures.testScope(this.coroutineContext)
        val singlePipelineRunner =
            PipelineRunner(
                reconciler,
                store,
                listOf(pipeline1),
                inputStreams,
                singlePipelineScope,
                aggregateDispatcher
            )

        // When - should complete without exception
        singlePipelineRunner.run()
        testScheduler.advanceUntilIdle()

        // Then
        coVerify(exactly = 1) { reconciler.run() }
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { store.hasStates() }
    }

    object Fixtures {
        fun testScope(ctx: CoroutineContext) = CoroutineScope(ctx + SupervisorJob())
    }
}
