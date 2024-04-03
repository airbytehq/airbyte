/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.core.util.WriteStreamConsumer
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DefaultWriteOperationExecutorTest {
    @Test
    internal fun `test that for each message in the iterator, an airbyte message is written to the output record consumer`() {
        val consumer: SerializedAirbyteMessageConsumer = mockk()
        val shutdownUtils: ShutdownUtils = mockk()
        val writeStreamConsumer: WriteStreamConsumer = mockk()

        every { consumer.close() } returns Unit
        every {
            shutdownUtils.stopOrphanedThreads(
                ShutdownUtils.EXIT_HOOK,
                ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
                ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
                TimeUnit.MINUTES,
            )
        } returns Unit
        every { writeStreamConsumer.consumeWriteStream() } returns Unit

        val executor =
            spyk<DefaultWriteOperationExecutor>(
                DefaultWriteOperationExecutor(
                    messageConsumer = consumer,
                    shutdownUtils = shutdownUtils,
                    writeStreamConsumer = writeStreamConsumer
                ),
            )

        val result = executor.execute()

        assertTrue(result.isSuccess)
        verify(exactly = 1) { consumer.close() }
        verify(exactly = 1) { writeStreamConsumer.consumeWriteStream() }
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
        val writeStreamConsumer: WriteStreamConsumer = mockk()

        every { messageConsumer.close() } returns Unit
        every { writeStreamConsumer.consumeWriteStream() } throws NullPointerException("test")
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
                writeStreamConsumer = writeStreamConsumer,
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
