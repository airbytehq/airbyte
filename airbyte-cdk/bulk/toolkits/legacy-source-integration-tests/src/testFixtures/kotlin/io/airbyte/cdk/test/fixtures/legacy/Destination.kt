package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}

interface Destination : Integration {
    /**
     * Return a consumer that writes messages to the destination.
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @param catalog
     * - schema of the incoming messages.
     * @return Consumer that accepts message. The [AirbyteMessageConsumer.accept] will be called n
     * times where n is the number of messages. [AirbyteMessageConsumer.close] will always be called
     * once regardless of success or failure.
     * @throws Exception
     * - any exception.
     */
    @Throws(Exception::class)
    fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer?

    /**
     * Default implementation allows us to not have to touch existing destinations while avoiding a
     * lot of conditional statements in [IntegrationRunner]. This is preferred over #getConsumer and
     * is the default Async Framework method.
     *
     * @param config config
     * @param catalog catalog
     * @param outputRecordCollector outputRecordCollector
     * @return AirbyteMessageConsumer wrapped in SerializedAirbyteMessageConsumer to maintain legacy
     * behavior.
     * @throws Exception exception
     */
    @Throws(Exception::class)
    fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        return ShimToSerializedAirbyteMessageConsumer(
            getConsumer(config, catalog, outputRecordCollector)
        )
    }

    /**
     * Backwards-compatibility wrapper for an AirbyteMessageConsumer. Strips the sizeInBytes
     * argument away from the .accept call.
     */
    class ShimToSerializedAirbyteMessageConsumer(private val consumer: AirbyteMessageConsumer?) :
        SerializedAirbyteMessageConsumer {
        @Throws(Exception::class)
        override fun start() {
            consumer!!.start()
        }

        /**
         * Consumes an [AirbyteMessage] for processing.
         *
         * If the provided JSON string is invalid AND represents a [AirbyteMessage.Type.STATE]
         * message, processing is halted. Otherwise, the invalid message is logged and execution
         * continues.
         *
         * @param message JSON representation of an [AirbyteMessage].
         * @throws Exception if an invalid state message is provided or the consumer is unable to
         * accept the provided message.
         */
        @Throws(Exception::class)
        override fun accept(message: String, sizeInBytes: Int) {
            consumeMessage(consumer, message)
        }

        @Throws(Exception::class)
        override fun close() {
            consumer!!.close()
        }

        /**
         * Custom class for parsing a JSON message to determine the type of the represented
         * [AirbyteMessage]. Do the bare minimum deserialisation by reading only the type field.
         */
        private class AirbyteTypeMessage {
            @get:JsonProperty("type")
            @set:JsonProperty("type")
            @JsonProperty("type")
            @JsonPropertyDescription("Message type")
            var type: AirbyteMessage.Type? = null
        }

        companion object {
            /**
             * Consumes an [AirbyteMessage] for processing.
             *
             * If the provided JSON string is invalid AND represents a [AirbyteMessage.Type.STATE]
             * message, processing is halted. Otherwise, the invalid message is logged and execution
             * continues.
             *
             * @param consumer An [AirbyteMessageConsumer] that can handle the provided message.
             * @param inputString JSON representation of an [AirbyteMessage].
             * @throws Exception if an invalid state message is provided or the consumer is unable
             * to accept the provided message.
             */
            @VisibleForTesting
            @Throws(Exception::class)
            fun consumeMessage(consumer: AirbyteMessageConsumer?, inputString: String) {
                val messageOptional = Jsons.tryDeserialize(inputString, AirbyteMessage::class.java)
                if (messageOptional.isPresent) {
                    consumer!!.accept(messageOptional.get())
                } else {
                    check(!isStateMessage(inputString)) { "Invalid state message: $inputString" }
                    LOGGER.error { "Received invalid message: $inputString" }
                }
            }

            /**
             * Tests whether the provided JSON string represents a state message.
             *
             * @param input a JSON string that represents an [AirbyteMessage].
             * @return `true` if the message is a state message, `false` otherwise.
             */
            private fun isStateMessage(input: String): Boolean {
                val deserialized = Jsons.tryDeserialize(input, AirbyteTypeMessage::class.java)
                return if (deserialized.isPresent) {
                    deserialized.get().type == AirbyteMessage.Type.STATE
                } else {
                    false
                }
            }
        }
    }

    val isV2Destination: Boolean
        /** Denotes if the destination fully supports Destinations V2. */
        get() = false

    companion object {
        @JvmStatic
        fun defaultOutputRecordCollector(message: AirbyteMessage?) {
            println(Jsons.serialize(message))
        }
    }
}
