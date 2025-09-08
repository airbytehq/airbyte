/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

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
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
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

    @MockK(relaxed = true) private lateinit var store: StateStore

    @MockK private lateinit var pipeline1: DataFlowPipeline

    @MockK private lateinit var pipeline2: DataFlowPipeline

    @MockK private lateinit var pipeline3: DataFlowPipeline

    private lateinit var runner: PipelineRunner

    @BeforeEach
    fun setup() {
        every { store.hasStates() } returns false
        runner = PipelineRunner(reconciler, store, listOf(pipeline1, pipeline2, pipeline3))
    }

    @Test
    fun `run should execute all pipelines concurrently`() = runTest {
        // Given
        coEvery { pipeline1.run() } coAnswers { delay(100) }
        coEvery { pipeline2.run() } coAnswers { delay(50) }
        coEvery { pipeline3.run() } coAnswers { delay(75) }

        // When
        val startTime = System.currentTimeMillis()
        runner.run()
        val endTime = System.currentTimeMillis()

        // Then
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { pipeline2.run() }
        coVerify(exactly = 1) { pipeline3.run() }

        // Verify they ran concurrently (total time should be close to the longest pipeline)
        // Allow some buffer for execution overhead
        assertTrue((endTime - startTime) < 200, "Pipelines should run concurrently")

        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should disable reconciler even when pipeline fails`() = runTest {
        // Given
        val exception = RuntimeException("Pipeline failed")
        coEvery { pipeline1.run() } throws exception
        val failingRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When/Then
        val thrownException = assertThrows<RuntimeException> { runBlocking { failingRunner.run() } }

        assertEquals("Pipeline failed", thrownException.message)

        // Verify reconciler was still disabled in finally block
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should execute operations in correct order`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When
        singlePipelineRunner.run()

        // Then - verify order of operations
        coVerifySequence {
            reconciler.run(any())
            pipeline1.run()
            reconciler.disable()
            reconciler.flushCompleteStates()
        }
    }

    @Test
    fun `run should pass correct CoroutineScope to reconciler`() = runTest {
        // Given
        var capturedScope: CoroutineScope? = null

        every { reconciler.run(any()) } answers { capturedScope = firstArg() }

        val emptyRunner = PipelineRunner(reconciler, store, emptyList())

        // When
        emptyRunner.run()

        // Then
        assertTrue(capturedScope != null, "CoroutineScope should be passed to reconciler")
        // Verify it's using IO dispatcher
        assertTrue(capturedScope.toString().contains("Dispatchers.IO"), "Should use IO dispatcher")
    }

    @Test
    fun `run should handle single pipeline`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When
        singlePipelineRunner.run()

        // Then
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should handle reconciler disable failure`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        coEvery { reconciler.disable() } throws RuntimeException("Failed to disable")
        val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When/Then
        val exception =
            assertThrows<RuntimeException> { runBlocking { singlePipelineRunner.run() } }

        assertEquals("Failed to disable", exception.message)

        // Verify pipeline was executed before the failure
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run should handle reconciler flushCompleteStates failure`() = runTest {
        // Given
        coEvery { pipeline1.run() } just Runs
        every { reconciler.flushCompleteStates() } throws RuntimeException("Failed to flush")
        val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When/Then
        val exception =
            assertThrows<RuntimeException> { runBlocking { singlePipelineRunner.run() } }

        assertEquals("Failed to flush", exception.message)

        // Verify everything up to flush was executed
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `pipelines property should return the list of pipelines`() {
        // When
        val result = runner.pipelines

        // Then
        assertEquals(3, result.size)
        assertEquals(pipeline1, result[0])
        assertEquals(pipeline2, result[1])
        assertEquals(pipeline3, result[2])
    }

    @Test
    fun `run should handle large number of pipelines`() = runTest {
        // Given
        val pipelines =
            (1..100).map {
                @MockK val pipeline = io.mockk.mockk<DataFlowPipeline>()
                coEvery { pipeline.run() } just Runs
                pipeline
            }

        val largeRunner = PipelineRunner(reconciler, store, pipelines)

        // When
        largeRunner.run()

        // Then
        pipelines.forEach { pipeline -> coVerify(exactly = 1) { pipeline.run() } }
        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
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

        val twoRunner = PipelineRunner(reconciler, store, listOf(pipeline1, pipeline2))

        // When
        twoRunner.run()

        // Then
        assertTrue(reconcilerDisabled, "Reconciler should have been disabled")
    }

    @Test
    fun `run should throw IllegalStateException when unflushed states exist at sync end`() =
        runTest {
            // Given
            coEvery { pipeline1.run() } just Runs
            every { store.hasStates() } returns true // Simulate unflushed states exist

            val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

            // When/Then
            val exception =
                assertThrows<IllegalStateException> { runBlocking { singlePipelineRunner.run() } }

            // Then
            assertEquals("Sync completed, but unflushed states were detected.", exception.message)

            // Verify all operations completed before the check
            coVerify(exactly = 1) { reconciler.run(any()) }
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

        val singlePipelineRunner = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When - should complete without exception
        singlePipelineRunner.run()

        // Then
        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { store.hasStates() }
    }
}
