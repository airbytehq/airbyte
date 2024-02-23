/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.config.AirbyteConfiguredCatalog
import io.airbyte.cdk.core.consumers.SerializedAirbyteMessageConsumerFactory
import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.commons.resources.MoreResources
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.BufferedInputStream
import java.io.FileInputStream
import java.util.Optional
import java.util.concurrent.TimeUnit

class DefaultWriteOperationExecutorTest {

    @Test
    internal fun `test that for each message in the iterator, an airbyte message is written to the output record consumer`() {
        val catalog: AirbyteConfiguredCatalog = mockk()
        val consumer: SerializedAirbyteMessageConsumer = mockk()
        val inputStream = BufferedInputStream(FileInputStream(MoreResources.readResourceAsFile("write-operation-input.txt")))
        val messageConsumerFactory: SerializedAirbyteMessageConsumerFactory = mockk()
        val messageConsumerFactoryOptional: Optional<SerializedAirbyteMessageConsumerFactory> = Optional.of(messageConsumerFactory)
        val shutdownUtils: ShutdownUtils = mockk()

        every { catalog.getConfiguredCatalog() } returns mockk()
        every { consumer.close() } returns Unit
        every { consumer.start() } returns Unit
        every { consumer.accept(any(), any()) } returns Unit
        every { messageConsumerFactory.createMessageConsumer(catalog.getConfiguredCatalog()) } returns consumer
        every { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) } returns Unit

        val executor = spyk<DefaultWriteOperationExecutor>(DefaultWriteOperationExecutor(catalog=catalog,
            messageConsumerFactory=messageConsumerFactoryOptional, shutdownUtils=shutdownUtils))

        every { executor.getInputStream() } returns inputStream

        val result = executor.execute()

        assertTrue(result.isSuccess)
        verify(exactly=13) { consumer.accept(any(), any()) }
        verify(exactly=1) { consumer.close() }
        verify(exactly=1) { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) }
    }

    @Test
    internal fun `test that if during writing an exception is raised, a failure result is returned`() {
        val catalog: AirbyteConfiguredCatalog = mockk()
        val messageConsumerFactory: SerializedAirbyteMessageConsumerFactory = mockk()
        val messageConsumerFactoryOptional: Optional<SerializedAirbyteMessageConsumerFactory> = Optional.of(messageConsumerFactory)
        val shutdownUtils: ShutdownUtils = mockk()

        every { catalog.getConfiguredCatalog() } returns mockk()
        every { messageConsumerFactory.createMessageConsumer(catalog.getConfiguredCatalog()) } throws NullPointerException("test")
        every { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) } returns Unit

        val executor = DefaultWriteOperationExecutor(catalog=catalog,
            messageConsumerFactory=messageConsumerFactoryOptional, shutdownUtils=shutdownUtils)

        val result = executor.execute()

        assertTrue(result.isFailure)
        verify(exactly=1) { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) }
    }

    @Test
    internal fun `test that if the message consumer factory is not present, a failure result is returned`() {
        val catalog: AirbyteConfiguredCatalog = mockk()
        val messageConsumerFactoryOptional: Optional<SerializedAirbyteMessageConsumerFactory> = Optional.empty()
        val shutdownUtils: ShutdownUtils = mockk()

        every { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) } returns Unit

        val executor = DefaultWriteOperationExecutor(catalog=catalog,
            messageConsumerFactory=messageConsumerFactoryOptional, shutdownUtils=shutdownUtils)

        val result = executor.execute()

        assertTrue(result.isFailure)
        verify(exactly=1) { shutdownUtils.stopOrphanedThreads(
            ShutdownUtils.EXIT_HOOK,
            ShutdownUtils.INTERRUPT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES,
            ShutdownUtils.EXIT_THREAD_DELAY_MINUTES,
            TimeUnit.MINUTES) }
    }
}