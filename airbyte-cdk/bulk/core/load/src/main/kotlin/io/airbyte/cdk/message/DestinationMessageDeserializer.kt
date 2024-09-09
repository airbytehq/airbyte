/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.util.Jsons
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
        try {
            val node = Jsons.readTree(serialized)
            val airbyteMessage = Jsons.treeToValue(node, AirbyteMessage::class.java)
            return messageFactory.fromAirbyteMessage(airbyteMessage, serialized)
        } catch (t: Throwable) {
            throw RuntimeException("Failed to deserialize AirbyteMessage")
        }
    }
}
