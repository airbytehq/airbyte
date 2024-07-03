/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.async.deser

import com.fasterxml.jackson.databind.exc.ValueInstantiationException
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class AirbyteMessageDeserializer(
    private val dataTransformer: StreamAwareDataTransformer = IdentityDataTransformer(),
) {
    class UnrecognizedAirbyteMessageTypeException(private val unrecognizedType: String) :
        Exception(unrecognizedType) {
        override fun toString(): String {
            return "Could not deserialize AirbyteMessage: unrecognized type: $unrecognizedType"
        }
    }

    /**
     * Deserializes to a [PartialAirbyteMessage] which can represent both a Record, State, or Trace
     * Message.
     *
     * Throws on deserialization errors, obfuscating the error message to avoid data leakage. In
     * recoverable cases (currently only when the top-level message type is unrecognized), throws a
     * dedicated exception.
     *
     * PartialAirbyteMessage holds either:
     * * entire serialized message string when message is a valid State Message
     * * serialized AirbyteRecordMessage when message is a valid Record Message
     *
     * @param message the string to deserialize
     * @return PartialAirbyteMessage if the message is valid
     */
    fun deserializeAirbyteMessage(
        message: String?,
    ): PartialAirbyteMessage {
        // TODO: This is doing some sketchy assumptions by deserializing either the whole or the
        // partial based on type.
        // Use JsonSubTypes and extend StdDeserializer to properly handle this.
        // Make immutability a first class citizen in the PartialAirbyteMessage class.
        val partial =
            try {
                Jsons.deserializeExactUnchecked(message, PartialAirbyteMessage::class.java)
            } catch (e: ValueInstantiationException) {
                // This is a hack to catch unrecognized message types. Jackson supports
                // the equivalent via annotations, but we cannot use them because the
                // AirbyteMessage
                // is generated from json-schema.
                val pat =
                    Regex("Cannot construct instance of .*AirbyteMessage.Type., problem: ([_A-Z]+)")
                val match = pat.find(e.message!!)
                if (match != null) {
                    val unrecognized = match.groups[1]?.value
                    logger.warn { "Unrecognized message type: $unrecognized" }
                    throw UnrecognizedAirbyteMessageTypeException(unrecognized!!)
                } else {
                    val obfuscated = Jsons.obfuscateDeserializationException(e)
                    throw RuntimeException(
                        "ValueInstantiationException when deserializing PartialAirbyteMessage: $obfuscated"
                    )
                }
            } catch (e: Exception) {
                val obfuscated = Jsons.obfuscateDeserializationException(e)
                throw RuntimeException("Could not deserialize PartialAirbyteMessage: $obfuscated")
            }

        val msgType = partial.type
        if (AirbyteMessage.Type.RECORD == msgType && partial.record?.data != null) {
            // Transform data provided by destination.
            val transformedData =
                dataTransformer.transform(
                    partial.record?.streamDescriptor,
                    partial.record?.data,
                    partial.record?.meta,
                )
            // store serialized json & meta
            partial.withSerialized(Jsons.serialize(transformedData.first))
            partial.record?.meta = transformedData.second
            // The connector doesn't need to be able to access to the record value. We can serialize
            // it here and
            // drop the json
            // object. Having this data stored as a string is slightly more optimal for the memory
            // usage.
            partial.record?.data = null
        } else if (AirbyteMessage.Type.STATE == msgType) {
            partial.withSerialized(message)
        } else if (AirbyteMessage.Type.TRACE != msgType) {
            logger.warn { "Unsupported message type: $msgType" }
        }

        return partial
    }
}
