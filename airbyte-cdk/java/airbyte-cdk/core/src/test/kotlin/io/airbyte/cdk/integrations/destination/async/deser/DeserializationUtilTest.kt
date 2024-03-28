/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.deser

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.math.BigDecimal
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DeserializationUtilTest {

    companion object {
        private const val SCHEMA_NAME = "public"
        private const val STREAM_NAME = "id_and_name"
        private val STREAM1_DESC: StreamDescriptor =
            StreamDescriptor().withNamespace(SCHEMA_NAME).withName(STREAM_NAME)

        private val PAYLOAD: JsonNode =
            Jsons.jsonNode(
                mapOf(
                    "created_at" to "2022-02-01T17:02:19+00:00",
                    "id" to 1,
                    "make" to "Mazda",
                    "nested_column" to mapOf("array_column" to listOf(1, 2, 3)),
                ),
            )

        private val STATE_MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    STREAM1_DESC,
                                )
                                .withStreamState(Jsons.jsonNode(1)),
                        ),
                )
    }

    private lateinit var deserializationUtil: DeserializationUtil
    private lateinit var streamAwareDataTransformer: StreamAwareDataTransformer

    @BeforeEach
    internal fun setup() {
        deserializationUtil = DeserializationUtil()
        streamAwareDataTransformer = IdentityDataTransformer()
    }

    @Test
    internal fun deserializeAirbyteMessageWithAirbyteRecord() {
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(PAYLOAD),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val airbyteRecordString = Jsons.serialize(PAYLOAD)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(airbyteRecordString, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithBigDecimalAirbyteRecord() {
        val payload =
            Jsons.jsonNode(
                mapOf(
                    "foo" to BigDecimal("1234567890.1234567890"),
                ),
            )
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(payload),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val airbyteRecordString = Jsons.serialize(payload)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(airbyteRecordString, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithEmptyAirbyteRecord() {
        val emptyMap: Map<*, *> = java.util.Map.of<Any, Any>()
        val airbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withNamespace(SCHEMA_NAME)
                        .withData(Jsons.jsonNode(emptyMap)),
                )
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(emptyMap.toString(), partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithNoStateOrRecord() {
        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.LOG).withLog(AirbyteLogMessage())
        val serializedAirbyteMessage = Jsons.serialize(airbyteMessage)
        assertThrows(
            RuntimeException::class.java,
        ) {
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        }
    }

    @Test
    internal fun deserializeAirbyteMessageWithAirbyteState() {
        val serializedAirbyteMessage = Jsons.serialize(STATE_MESSAGE1)
        val partial =
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        assertEquals(serializedAirbyteMessage, partial.serialized)
    }

    @Test
    internal fun deserializeAirbyteMessageWithBadAirbyteState() {
        val badState =
            AirbyteMessage()
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    STREAM1_DESC,
                                )
                                .withStreamState(Jsons.jsonNode(1)),
                        ),
                )
        val serializedAirbyteMessage = Jsons.serialize(badState)
        assertThrows(
            RuntimeException::class.java,
        ) {
            deserializationUtil.deserializeAirbyteMessage(
                serializedAirbyteMessage,
                streamAwareDataTransformer,
            )
        }
    }
}
