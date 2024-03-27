/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.function.Consumer
import org.junit.jupiter.api.Test
import org.mockito.Mockito

abstract class PerStreamStateMessageTest {
    protected abstract val mockedConsumer: Consumer<AirbyteMessage>
        get

    protected abstract val messageConsumer: FailureTrackingAirbyteMessageConsumer
        get

    @Test
    @Throws(Exception::class)
    fun ensureAllStateMessageAreEmitted() {
        val airbyteMessage1 =
            AirbyteMessageCreator.createStreamStateMessage("name_one", "state_one")
        val airbyteMessage2 =
            AirbyteMessageCreator.createStreamStateMessage("name_two", "state_two")
        val airbyteMessage3 =
            AirbyteMessageCreator.createStreamStateMessage("name_three", "state_three")
        val messageConsumer = messageConsumer

        messageConsumer.accept(airbyteMessage1)
        messageConsumer.accept(airbyteMessage2)
        messageConsumer.accept(airbyteMessage3)

        val mConsumer = mockedConsumer
        val inOrder = Mockito.inOrder(mConsumer)

        inOrder.verify(mConsumer).accept(airbyteMessage1)
        inOrder.verify(mConsumer).accept(airbyteMessage2)
        inOrder.verify(mConsumer).accept(airbyteMessage3)
    }

    internal object AirbyteMessageCreator {
        fun createStreamStateMessage(name: String?, value: String): AirbyteMessage {
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor().withName(name))
                                .withStreamState(Jsons.jsonNode(value))
                        )
                )
        }
    }
}
