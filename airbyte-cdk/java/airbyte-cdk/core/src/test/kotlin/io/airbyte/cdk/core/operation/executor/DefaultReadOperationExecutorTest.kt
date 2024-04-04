/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.util.Optional
import java.util.concurrent.TimeUnit
import java.util.function.Consumer

class DefaultReadOperationExecutorTest {
    @Test
    internal fun `test that for each message in the iterator, an airbyte message is written to the output record consumer`() {
        val iterator: AutoCloseableIterator<AirbyteMessage> = mockk()
        val messageIterator = Optional.of(iterator)
        val outputRecordCollector: Consumer<AirbyteMessage> = mockk()
        val shutdownUtils: ShutdownUtils = mockk()

        every { iterator.airbyteStream } returns Optional.of(AirbyteStreamNameNamespacePair("name", "namespace"))
        every { iterator.close() } returns Unit
        every { iterator.forEachRemaining(outputRecordCollector) } returns Unit
        every { outputRecordCollector.accept(any()) } returns Unit
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
            DefaultReadOperationExecutor(
                messageIterator = messageIterator,
                outputRecordCollector = outputRecordCollector,
                shutdownUtils = shutdownUtils,
            )

        val result = executor.execute()

        assertTrue(result.isSuccess)
        verify(exactly = 1) { iterator.forEachRemaining(outputRecordCollector) }
        verify(exactly = 1) { iterator.close() }
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
    internal fun `test that if during message iteration an exception is raised, a failure result is returned`() {
        val iterator: AutoCloseableIterator<AirbyteMessage> = mockk()
        val messageIterator = Optional.of(iterator)
        val outputRecordCollector: Consumer<AirbyteMessage> = mockk()
        val shutdownUtils: ShutdownUtils = mockk()

        every { iterator.airbyteStream } returns Optional.of(AirbyteStreamNameNamespacePair("name", "namespace"))
        every { iterator.close() } returns Unit
        every { iterator.forEachRemaining(outputRecordCollector) } throws NullPointerException("test")
        every { outputRecordCollector.accept(any()) } returns Unit
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
            DefaultReadOperationExecutor(
                messageIterator = messageIterator,
                outputRecordCollector = outputRecordCollector,
                shutdownUtils = shutdownUtils,
            )

        val result = executor.execute()

        assertTrue(result.isFailure)
        verify(exactly = 1) { iterator.close() }
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
    internal fun `test that if the message iterator is not present, a failure result is returned`() {
        val messageIterator = Optional.empty<AutoCloseableIterator<AirbyteMessage>>()
        val outputRecordCollector: Consumer<AirbyteMessage> = mockk()
        val shutdownUtils: ShutdownUtils = mockk()

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
            DefaultReadOperationExecutor(
                messageIterator = messageIterator,
                outputRecordCollector = outputRecordCollector,
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
