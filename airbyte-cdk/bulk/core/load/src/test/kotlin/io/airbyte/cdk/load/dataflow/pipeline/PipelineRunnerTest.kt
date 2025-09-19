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
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.test.currentTime
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
    fun `run executes pipelines concurrently (virtual time)`() = runTest {
        // Given: different delays to ensure concurrency; virtual time will advance
        coEvery { pipeline1.run() } coAnswers { delay(100) }
        coEvery { pipeline2.run() } coAnswers { delay(50) }
        coEvery { pipeline3.run() } coAnswers { delay(75) }

        val t0 = currentTime

        // When
        runner.run()

        val elapsed = currentTime - t0

        // Then
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { pipeline2.run() }
        coVerify(exactly = 1) { pipeline3.run() }

        // In virtual time, total elapsed should be ~max(delay) = 100
        assertTrue(
            elapsed in 100..130,
            "Elapsed virtual time ($elapsed) should be close to the longest pipeline (100ms)"
        )

        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run disables reconciler and does not flush when a pipeline fails (fail fast)`() = runTest {
        // Given
        val exception = RuntimeException("Pipeline failed")
        coEvery { pipeline1.run() } coAnswers
            {
                delay(10)
                throw exception
            }

        // Make others "long running" so we can verify they get cancelled
        var p2Cancelled = false
        coEvery { pipeline2.run() } coAnswers
            {
                try {
                    delay(10_000)
                } finally {
                    p2Cancelled = true
                }
            }
        var p3Cancelled = false
        coEvery { pipeline3.run() } coAnswers
            {
                try {
                    delay(10_000)
                } finally {
                    p3Cancelled = true
                }
            }

        // When/Then
        val thrown = assertThrows<RuntimeException> { runBlocking { runner.run() } }
        assertEquals("Pipeline failed", thrown.message)

        // Verify fail-fast cancellation reached siblings
        assertTrue(p2Cancelled, "pipeline2 should be cancelled when pipeline1 fails")
        assertTrue(p3Cancelled, "pipeline3 should be cancelled when pipeline1 fails")

        // Verify reconciler was still disabled in finally block
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `run executes operations in correct order for single pipeline success`() {
        // Given
        coEvery { pipeline1.run() } just Runs
        val single = PipelineRunner(reconciler, store, listOf(pipeline1))

        // When
        runBlocking { single.run() }

        // Then
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

        assertTrue(capturedScope != null, "CoroutineScope should be passed to reconciler")
        // No assertion about dispatcher — implementation intentionally uses parent scope.
    }

    @Test
    fun `handles single pipeline success`() = runTest {
        coEvery { pipeline1.run() } just Runs
        val single = PipelineRunner(reconciler, store, listOf(pipeline1))
        single.run()

        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `propagates failure from reconciler disable`() = runTest {
        coEvery { pipeline1.run() } just Runs
        coEvery { reconciler.disable() } throws RuntimeException("Failed to disable")
        val single = PipelineRunner(reconciler, store, listOf(pipeline1))

        val ex = assertThrows<RuntimeException> { runBlocking { single.run() } }
        assertEquals("Failed to disable", ex.message)

        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 0) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `propagates failure from reconciler flushCompleteStates`() {
        coEvery { pipeline1.run() } just Runs
        every { reconciler.flushCompleteStates() } throws RuntimeException("Failed to flush")
        val single = PipelineRunner(reconciler, store, listOf(pipeline1))

        val ex = assertThrows<RuntimeException> { runBlocking { single.run() } }
        assertEquals("Failed to flush", ex.message)

        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `pipelines property returns list`() {
        val result = runner.pipelines
        assertEquals(3, result.size)
        assertEquals(pipeline1, result[0])
        assertEquals(pipeline2, result[1])
        assertEquals(pipeline3, result[2])
    }

    @Test
    fun `large number of pipelines succeeds`() = runTest {
        val many =
            (1..100).map {
                val p = io.mockk.mockk<DataFlowPipeline>()
                coEvery { p.run() } just Runs
                p
            }
        val largeRunner = PipelineRunner(reconciler, store, many)
        largeRunner.run()

        many.forEach { p -> coVerify(exactly = 1) { p.run() } }
        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `reconciler is disabled only after all pipelines complete on success`() = runTest {
        var p1Done = false
        var p2Done = false
        var disabledAfter = false

        coEvery { pipeline1.run() } coAnswers
            {
                delay(100)
                p1Done = true
            }
        coEvery { pipeline2.run() } coAnswers
            {
                delay(50)
                p2Done = true
            }
        coEvery { reconciler.disable() } answers { disabledAfter = p1Done && p2Done }

        val two = PipelineRunner(reconciler, store, listOf(pipeline1, pipeline2))
        two.run()

        assertTrue(disabledAfter, "reconciler.disable should run after both pipelines finish")
    }

    @Test
    fun `throws IllegalStateException when unflushed states exist on success`() = runTest {
        coEvery { pipeline1.run() } just Runs
        every { store.hasStates() } returns true

        val single = PipelineRunner(reconciler, store, listOf(pipeline1))
        val ex = assertThrows<IllegalStateException> { runBlocking { single.run() } }

        assertEquals("Sync completed, but unflushed states were detected.", ex.message)

        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { store.hasStates() }
    }

    @Test
    fun `does not throw when all states are flushed on success`() = runTest {
        coEvery { pipeline1.run() } just Runs
        every { store.hasStates() } returns false
        val single = PipelineRunner(reconciler, store, listOf(pipeline1))

        single.run()

        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { pipeline1.run() }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { store.hasStates() }
    }

    @Test
    fun `no pipelines still runs reconciler lifecycle`() = runTest {
        val emptyRunner = PipelineRunner(reconciler, store, emptyList())
        emptyRunner.run()

        coVerify(exactly = 1) { reconciler.run(any()) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
        coVerify(exactly = 1) { store.hasStates() }
    }

    @Test
    fun `when multiple pipelines fail, first failure is propagated and others are cancelled`() =
        runTest {
            // pipeline1 fails first
            val first = IllegalStateException("first")
            coEvery { pipeline1.run() } coAnswers
                {
                    delay(10)
                    throw first
                }

            // pipeline2 fails later, but should be cancelled before throwing
            var p2Cancelled = false
            coEvery { pipeline2.run() } coAnswers
                {
                    try {
                        delay(10_000) // should be cancelled before it fails
                    } catch (e: CancellationException) {
                        p2Cancelled = true
                    }
                }

            // pipeline3 hangs; we assert it was cancelled in finally
            var p3Cancelled = false
            coEvery { pipeline3.run() } coAnswers
                {
                    try {
                        suspendCancellableCoroutine<Unit> { /* never resumes */}
                    } finally {
                        p3Cancelled = true
                    }
                }

            val ex = assertThrows<IllegalStateException> { runBlocking { runner.run() } }

            assertEquals("first", ex.message)

            assertTrue(p2Cancelled, "pipeline2 should be cancelled due to first failure")
            assertTrue(p3Cancelled, "pipeline3 should be cancelled due to first failure")

            coVerify(exactly = 1) { reconciler.disable() }
            coVerify(exactly = 0) { reconciler.flushCompleteStates() }
        }
}
