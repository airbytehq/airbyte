/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination_async.deser

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage

object DeserializationUtil {
    /**
     * Deserializes to a [PartialAirbyteMessage] which can represent both a Record or a State
     * Message
     *
     * PartialAirbyteMessage holds either:
     * * entire serialized message string when message is a valid State Message
     * * serialized AirbyteRecordMessage when message is a valid Record Message
     *
     * @param messageString the string to deserialize
     * @return PartialAirbyteMessage if the message is valid, empty otherwise
     */
    @JvmStatic
    @VisibleForTesting
    fun deserializeAirbyteMessage(
        messageString: String?,
        dataTransformer: StreamAwareDataTransformer
    ): PartialAirbyteMessage {
        // TODO: This is doing some sketchy assumptions by deserializing either the whole or the
        // partial based on type.
        // Use JsonSubTypes and extend StdDeserializer to properly handle this.
        // Make immutability a first class citizen in the PartialAirbyteMessage class.
        val partial =
            Jsons.tryDeserializeExact(messageString, PartialAirbyteMessage::class.java)
                .orElseThrow { RuntimeException("Unable to deserialize PartialAirbyteMessage.") }

        val msgType = partial.type
        if (AirbyteMessage.Type.RECORD == msgType && partial.record.data != null) {
            // Transform data provided by destination.
            val transformedData =
                dataTransformer.transform(
                    partial.record.streamDescriptor,
                    partial.record.data,
                    partial.record.meta
                )
            // store serialized json & meta
            partial.withSerialized(Jsons.serialize(transformedData.getLeft()))
            partial.record.meta = transformedData.getRight()
            // The connector doesn't need to be able to access to the record value. We can serialize
            // it here and
            // drop the json
            // object. Having this data stored as a string is slightly more optimal for the memory
            // usage.
            partial.record.data = null
        } else if (AirbyteMessage.Type.STATE == msgType) {
            partial.withSerialized(messageString)
        } else {
            throw RuntimeException(String.format("Unsupported message type: %s", msgType))
        }

        return partial
    }
}
