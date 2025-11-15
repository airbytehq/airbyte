/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor

class NonResumableStateMessageProducer<T>(
    private val isCdc: Boolean,
    private val sourceStateMessageProducer: SourceStateMessageProducer<T>
) : SourceStateMessageProducer<AirbyteMessage> {
    override fun generateStateMessageAtCheckpoint(
        stream: ConfiguredAirbyteStream?
    ): AirbyteStateMessage? {
        return null
    }

    override fun processRecordMessage(
        stream: ConfiguredAirbyteStream?,
        message: AirbyteMessage
    ): AirbyteMessage {
        return message
    }

    override fun createFinalStateMessage(stream: ConfiguredAirbyteStream?): AirbyteStateMessage? {
        if (isCdc) {
            return sourceStateMessageProducer.createFinalStateMessage(stream)
        } else {
            val airbyteStreamState =
                AirbyteStreamState()
                    .withStreamDescriptor(
                        StreamDescriptor()
                            .withName(stream!!.stream.name)
                            .withNamespace(stream.stream.namespace),
                    )

            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(airbyteStreamState)
        }
    }

    // no intermediate state message.
    override fun shouldEmitStateMessage(stream: ConfiguredAirbyteStream?): Boolean {
        return false
    }
}
