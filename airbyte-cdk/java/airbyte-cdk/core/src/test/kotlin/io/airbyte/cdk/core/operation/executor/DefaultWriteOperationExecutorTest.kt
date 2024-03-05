/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.commons.resources.MoreResources
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import java.io.BufferedInputStream
import java.io.FileInputStream
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultWriteOperationExecutorTest {
    @Test
    internal fun `test that for each message in the iterator, an airbyte message is written to the output record consumer`() {
        val consumer: SerializedAirbyteMessageConsumer = mockk()
        val inputStream =
            BufferedInputStream(
                FileInputStream(MoreResources.readResourceAsFile("write-operation-input.txt"))
            )
        val shutdownUtils: ShutdownUtils = mockk()

        every { consumer.close() } returns Unit
        every { consumer.start() } returns Unit
        every { consumer.accept(any(), any()) } returns Unit
        every {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        } returns Unit

        val executor =
            spyk<DefaultWriteOperationExecutor>(
                DefaultWriteOperationExecutor(
                    messageConsumer = consumer,
                    shutdownUtils = shutdownUtils,
                ),
            )

        every { executor.getInputStream() } returns inputStream

        val result = executor.execute()

        assertTrue(result.isSuccess)
        verify(exactly = 13) { consumer.accept(any(), any()) }
        verify(exactly = 1) { consumer.close() }
        verify(exactly = 1) {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        }
    }

    @Test
    internal fun `test that if during writing an exception is raised, a failure result is returned`() {
        val messageConsumer: SerializedAirbyteMessageConsumer = mockk()
        val shutdownUtils: ShutdownUtils = mockk()

        every { messageConsumer.close() } returns Unit
        every { messageConsumer.start() } throws NullPointerException("test")
        every {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        } returns Unit

        val executor =
            DefaultWriteOperationExecutor(
                messageConsumer = messageConsumer,
                shutdownUtils = shutdownUtils,
            )

        val result = executor.execute()

        assertTrue(result.isFailure)
        verify(exactly = 1) {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        }
    }
}
