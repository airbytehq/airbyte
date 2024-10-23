/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class DestinationMessageTest {
    private val factory =
        DestinationMessageFactory(
            DestinationCatalog(
                listOf(
                    DestinationStream(
                        descriptor,
                        Append,
                        ObjectTypeWithEmptySchema,
                        generationId = 42,
                        minimumGenerationId = 0,
                        syncId = 42,
                    )
                )
            )
        )

    @ParameterizedTest
    @MethodSource("roundTrippableMessages")
    fun testRoundTrip(message: AirbyteMessage) {
        val roundTripped =
            factory.fromAirbyteMessage(message, Jsons.serialize(message)).asProtocolMessage()
        Assertions.assertEquals(message, roundTripped)
    }

    // Checkpoint messages aren't round-trippable.
    // We don't read in destinationStats (because we're the ones setting that field).
    @Test
    fun testStreamCheckpoint() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(descriptor.asProtocolObject())
                                .withStreamState(blob1)
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                )

        val parsedMessage =
            factory.fromAirbyteMessage(inputMessage, Jsons.serialize(inputMessage))
                as StreamCheckpoint

        Assertions.assertEquals(
            inputMessage.also {
                it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0)
            },
            parsedMessage.withDestinationStats(CheckpointMessage.Stats(3)).asProtocolMessage(),
        )
    }

    @Test
    fun testGlobalCheckpoint() {
        val inputMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withGlobal(
                            AirbyteGlobalState()
                                .withSharedState(blob1)
                                .withStreamStates(
                                    listOf(
                                        AirbyteStreamState()
                                            .withStreamDescriptor(descriptor.asProtocolObject())
                                            .withStreamState(blob2),
                                    ),
                                ),
                        )
                        // Note: only source stats, no destination stats
                        .withSourceStats(AirbyteStateStats().withRecordCount(2.0))
                )

        val parsedMessage =
            factory.fromAirbyteMessage(
                inputMessage,
                Jsons.serialize(inputMessage),
            ) as GlobalCheckpoint

        Assertions.assertEquals(
            inputMessage.also {
                it.state.destinationStats = AirbyteStateStats().withRecordCount(3.0)
            },
            parsedMessage.withDestinationStats(CheckpointMessage.Stats(3)).asProtocolMessage(),
        )
    }

    companion object {
        private val descriptor = DestinationStream.Descriptor("namespace", "name")
        private val blob1 = Jsons.deserialize("""{"foo": "bar"}""")
        private val blob2 = Jsons.deserialize("""{"foo": "bar"}""")

        @JvmStatic
        fun roundTrippableMessages(): List<Arguments> =
            listOf(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withStream("name")
                                .withNamespace("namespace")
                                .withEmittedAt(1234)
                                .withMeta(
                                    AirbyteRecordMessageMeta()
                                        .withChanges(
                                            listOf(
                                                AirbyteRecordMessageMetaChange()
                                                    .withField("foo")
                                                    .withReason(
                                                        AirbyteRecordMessageMetaChange.Reason
                                                            .DESTINATION_FIELD_SIZE_LIMITATION
                                                    )
                                                    .withChange(
                                                        AirbyteRecordMessageMetaChange.Change.NULLED
                                                    )
                                            )
                                        )
                                )
                                .withData(blob1)
                        ),
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                .withEmittedAt(1234.0)
                                .withStreamStatus(
                                    AirbyteStreamStatusTraceMessage()
                                        // Intentionally no "reasons" here - destinations never
                                        // inspect that
                                        // field, so it's not round-trippable
                                        .withStreamDescriptor(descriptor.asProtocolObject())
                                        .withStatus(
                                            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
                                                .COMPLETE
                                        )
                                )
                        ),
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                .withEmittedAt(1234.0)
                                .withStreamStatus(
                                    AirbyteStreamStatusTraceMessage()
                                        // Intentionally no "reasons" here - destinations never
                                        // inspect that
                                        // field, so it's not round-trippable
                                        .withStreamDescriptor(descriptor.asProtocolObject())
                                        .withStatus(
                                            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
                                                .INCOMPLETE
                                        )
                                )
                        ),
                )
                .map { Arguments.of(it) }
    }
}
