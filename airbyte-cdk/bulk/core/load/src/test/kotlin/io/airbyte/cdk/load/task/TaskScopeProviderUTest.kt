/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.test.util.CoroutineTestUtils.Companion.assertDoesNotThrow
import io.airbyte.cdk.load.test.util.CoroutineTestUtils.Companion.assertThrows
import io.mockk.every
import io.mockk.impl.annotations.MockK
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class TaskScopeProviderUTest {
    val mockTimeout = 1000L
    @MockK(relaxed = true) lateinit var config: DestinationConfiguration

    private fun makeLoopingTask(terminalCondition: TerminalCondition) =
        object : Task {
            override val terminalCondition: TerminalCondition = terminalCondition
            override suspend fun execute() {
                while (true) {
                    delay(mockTimeout / 2)
                }
            }
        }

    @BeforeEach
    fun setup() {
        every { config.gracefulCancellationTimeoutMs } returns mockTimeout
    }

    @Test
    fun `test self-terminating tasks are not canceled`() = runTest {
        val completed = CompletableDeferred<Unit>()
        val selfTerminatingTask =
            object : Task {
                override val terminalCondition: TerminalCondition = SelfTerminating
                override suspend fun execute() {
                    completed.complete(Unit)
                }
            }
        val provider = TaskScopeProvider(config)
        launch {
                provider.launch(selfTerminatingTask)
                completed.await()
            }
            .join()
        assertDoesNotThrow { provider.close() }
    }

    @Test
    fun `test hung self-terminating task throws exception`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(SelfTerminating))
        assertThrows(TimeoutCancellationException::class) { provider.close() }
    }

    @Test
    fun `test cancel on sync success`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(OnEndOfSync))
        assertDoesNotThrow { provider.close() }
    }

    @Test
    fun `test cancel-on-failure not canceled on success`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(OnSyncFailureOnly))
        assertThrows(TimeoutCancellationException::class) { provider.close() }
    }

    @Test
    fun `test cancel-on-failure canceled on failure`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(OnSyncFailureOnly))
        assertDoesNotThrow { provider.kill() }
    }

    @Test
    fun `test cancel-at-end also canceled on failure`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(OnEndOfSync))
        assertDoesNotThrow { provider.kill() }
    }

    @Test
    fun `test hung self-terminating task does not throw on failure`() = runTest {
        val provider = TaskScopeProvider(config)
        provider.launch(makeLoopingTask(SelfTerminating))
        assertDoesNotThrow { provider.kill() }
    }
}
