/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayInputStream
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationMessageInputFlowTest {

    @Test
    fun `should deserialize and emit messages from input stream`() = runTest {
        // Given
        val line1 = "message1"
        val line2 = "message2"
        val inputStream = ByteArrayInputStream("$line1\n$line2\n".toByteArray())
        val deserializer = mockk<ProtocolMessageDeserializer>()
        val message1 = mockk<DestinationMessage>()
        val message2 = mockk<DestinationMessage>()

        every { deserializer.deserialize(line1) } returns message1
        every { deserializer.deserialize(line2) } returns message2

        val inputFlow = DestinationMessageInputFlow(inputStream, deserializer)
        val collector = mockk<FlowCollector<DestinationMessage>>(relaxed = true)

        // When
        inputFlow.collect(collector)

        // Then
        verify(exactly = 1) { deserializer.deserialize(line1) }
        verify(exactly = 1) { deserializer.deserialize(line2) }
        coVerify(exactly = 1) { collector.emit(message1) }
        coVerify(exactly = 1) { collector.emit(message2) }
    }

    @Test
    fun `should ignore empty lines`() = runTest {
        // Given
        val line1 = "message1"
        val emptyLine = ""
        val line2 = "message2"
        val inputStream = ByteArrayInputStream("$line1\n$emptyLine\n$line2\n".toByteArray())
        val deserializer = mockk<ProtocolMessageDeserializer>()
        val message1 = mockk<DestinationMessage>()
        val message2 = mockk<DestinationMessage>()

        every { deserializer.deserialize(line1) } returns message1
        every { deserializer.deserialize(line2) } returns message2

        val inputFlow = DestinationMessageInputFlow(inputStream, deserializer)
        val collector = mockk<FlowCollector<DestinationMessage>>(relaxed = true)

        // When
        inputFlow.collect(collector)

        // Then
        verify(exactly = 1) { deserializer.deserialize(line1) }
        verify(exactly = 0) { deserializer.deserialize(emptyLine) } // Ensure empty line is ignored
        verify(exactly = 1) { deserializer.deserialize(line2) }
        coVerify(exactly = 1) { collector.emit(message1) }
        coVerify(exactly = 1) { collector.emit(message2) }
    }

    @Test
    fun `should not emit if no record is present`() = runTest {
        // Given
        val inputStream = ByteArrayInputStream("".toByteArray())
        val deserializer = mockk<ProtocolMessageDeserializer>()

        val inputFlow = DestinationMessageInputFlow(inputStream, deserializer)
        val collector = mockk<FlowCollector<DestinationMessage>>(relaxed = true)

        // When
        inputFlow.collect(collector)

        // Then
        coVerify(exactly = 0) { collector.emit(any()) } // Ensure no other message is emitted
    }
}
