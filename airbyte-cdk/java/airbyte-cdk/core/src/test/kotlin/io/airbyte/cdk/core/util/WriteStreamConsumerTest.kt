/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.util

import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.commons.resources.MoreResources
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.BufferedInputStream
import java.io.FileInputStream
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class WriteStreamConsumerTest {

    @Test
    internal fun testThatEachMessageIsWrittenToTheConsumer() {
        val consumer: SerializedAirbyteMessageConsumer = mockk()
        val inputStream =
            BufferedInputStream(
                FileInputStream(MoreResources.readResourceAsFile("write-operation-input.txt"))
            )
        every { consumer.start() } returns Unit
        every { consumer.accept(any(), any()) } returns Unit
        val writeStream = WriteStreamConsumer(consumer = consumer)

        writeStream.consumeWriteStream(inputStream = inputStream)
        verify(exactly = 13) { consumer.accept(any(), any()) }
        verify(exactly = 1) { consumer.start() }
        verify(exactly = 0) { consumer.close() }
    }

    @Test
    internal fun testThatTheWriteStreamConsumerDoesntSwallowExceptions() {
        val messageConsumer: SerializedAirbyteMessageConsumer = mockk()
        every { messageConsumer.start() } throws NullPointerException("test")

        val writeStreamConsumer = WriteStreamConsumer(consumer = messageConsumer)

        assertThrows<NullPointerException> { writeStreamConsumer.consumeWriteStream() }
    }
}
