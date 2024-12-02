/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.protocol.models.v0.AirbyteMessage
import jakarta.inject.Singleton

interface Deserializer<T : Any> {
    fun deserialize(serialized: String): T
}

/**
 * Converts the internal @[AirbyteMessage] to the internal @[DestinationMessage] Ideally, this would
 * not use protocol messages at all, but rather a specialized deserializer for routing.
 */
@Singleton
class DefaultDestinationMessageDeserializer(private val messageFactory: DestinationMessageFactory) :
    Deserializer<DestinationMessage> {

    override fun deserialize(serialized: String): DestinationMessage {
        val airbyteMessage =
            try {
                serialized.deserializeToClass(AirbyteMessage::class.java)
            } catch (t: Throwable) {
                /**
                 * We don't want to expose client data, but we'd like to get as much info as we can
                 * about these malformed messages.
                 */
                val type =
                    if (serialized.contains("RECORD")) {
                        "record"
                    } else if (serialized.contains("STATE")) {
                        "state"
                    } else if (serialized.contains("TRACE")) {
                        if (serialized.contains("STATUS", ignoreCase = true)) {
                            "status"
                        } else {
                            "trace"
                        }
                    } else {
                        "unknown"
                    }

                throw RuntimeException(
                    "Failed to deserialize airbyte message (type=$type; length=${serialized.length}; reason=${t.javaClass})"
                )
            }

        val internalDestinationMessage =
            try {
                messageFactory.fromAirbyteMessage(airbyteMessage, serialized)
            } catch (t: Throwable) {
                throw RuntimeException("Failed to convert AirbyteMessage to DestinationMessage", t)
            }

        return internalDestinationMessage
    }
}
