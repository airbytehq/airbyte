/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

class StatePublisherTest {
    @Test
    fun `test publish`() {
        val consumer = mockk<OutputConsumer>(relaxed = true)
        val message = mockk<CheckpointMessage>()
        val protocolMessage = mockk<AirbyteMessage>()
        every { message.asProtocolMessage() } returns protocolMessage

        val statePublisher = StatePublisher(consumer)
        statePublisher.publish(message)

        verify { consumer.accept(protocolMessage) }
    }
}
