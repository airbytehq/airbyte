/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.protocol.models.v0.AirbyteMessage
import jakarta.inject.Singleton

/**
 * Converts the internal @[AirbyteMessage] to the internal @[DestinationMessage] Ideally, this would
 * not use protocol messages at all, but rather a specialized deserializer for routing.
 */
@Singleton
class ProtocolMessageDeserializer(
    private val destinationMessageFactory: DestinationMessageFactory,
) {
    fun deserialize(
        serialized: String,
    ): DestinationMessage {
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

        return destinationMessageFactory.fromAirbyteMessage(
            airbyteMessage,
            serialized,
        )
    }
}
