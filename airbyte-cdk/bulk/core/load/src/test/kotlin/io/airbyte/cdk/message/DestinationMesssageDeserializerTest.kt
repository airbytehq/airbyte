/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Prototype
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(environments = ["DestinationMesssageDeserializerTest"])
class DestinationMesssageDeserializerTest {
    @Factory
    class CatalogProvider {

        @Prototype
        @Replaces(DestinationCatalog::class)
        @Requires(env = ["DestinationMesssageDeserializerTest"])
        fun make(): DestinationCatalog {
            return DestinationCatalog(
                streams =
                    listOf("stream_name1", "stream_name2", "stream_name3").map {
                        DestinationStream(
                            descriptor =
                                DestinationStream.Descriptor(
                                    namespace = "stream_namespace",
                                    name = it
                                )
                        )
                    }
            )
        }
    }

    class RecordMessageFactory(
        val namespace: String = "stream_namespace",
        val name: String = "stream_name1",
        val emittedAtMs: Long = System.currentTimeMillis(),
        val testData: JsonNode = JsonNodeFactory.instance.objectNode().put("type", "object"),
        val serialized: String
    ) {
        fun make(): Pair<AirbyteMessage, DestinationMessage> {
            val input =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withNamespace(namespace)
                            .withStream(name)
                            .withEmittedAt(emittedAtMs)
                            .withData(testData)
                    )
            val expectedOutput =
                DestinationRecord(
                    stream =
                        DestinationStream(
                            descriptor =
                                DestinationStream.Descriptor(namespace = namespace, name = name)
                        ),
                    emittedAtMs = emittedAtMs,
                    data = testData,
                    serialized = serialized
                )
            return Pair(input, expectedOutput)
        }
    }

    class EndOfStreamMessageFactory(
        val namespace: String = "stream_namespace",
        val name: String = "stream_name1",
        val emittedAtMs: Long = System.currentTimeMillis()
    ) {
        fun make(): Pair<AirbyteMessage, DestinationMessage> {
            val input =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withEmittedAt(emittedAtMs.toDouble())
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(
                                        StreamDescriptor().withNamespace(namespace).withName(name)
                                    )
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            val expectedOutput =
                DestinationStreamComplete(
                    stream =
                        DestinationStream(
                            descriptor =
                                DestinationStream.Descriptor(
                                    namespace = namespace,
                                    name = name,
                                ),
                        ),
                    emittedAtMs = emittedAtMs
                )
            return Pair(input, expectedOutput)
        }
    }

    class StreamStateMessageFactory(
        val namespace: String = "stream_namespace",
        val name: String = "stream_name1",
        val state: JsonNode = JsonNodeFactory.instance.objectNode().put("type", "object"),
        val recordCount: Long = 1001,
    ) {
        fun make(): Pair<AirbyteMessage, DestinationMessage> {
            val input =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withSourceStats(
                                AirbyteStateStats().withRecordCount(recordCount.toDouble())
                            )
                            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                            .withStream(
                                AirbyteStreamState()
                                    .withStreamState(state)
                                    .withStreamDescriptor(
                                        StreamDescriptor().withNamespace(namespace).withName(name)
                                    )
                            )
                    )
            val expectedOutput =
                DestinationStreamState(
                    streamState =
                        DestinationStateMessage.StreamState(
                            stream =
                                DestinationStream(
                                    descriptor =
                                        DestinationStream.Descriptor(
                                            namespace = namespace,
                                            name = name
                                        )
                                ),
                            state = state
                        ),
                    sourceStats = DestinationStateMessage.Stats(recordCount = recordCount)
                )
            return Pair(input, expectedOutput)
        }
    }

    class GlobalStateMessageFactory(
        val state: JsonNode = JsonNodeFactory.instance.objectNode().put("type", "object"),
        val recordCount: Long = 1001,
        val streams: List<Pair<String, String>> =
            listOf(
                Pair("stream_namespace", "stream_name1"),
                Pair("stream_namespace", "stream_name2"),
                Pair("stream_namespace", "stream_name3")
            )
    ) {
        fun make(): Pair<AirbyteMessage, DestinationMessage> {
            val input =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withSourceStats(
                                AirbyteStateStats().withRecordCount(recordCount.toDouble())
                            )
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(state)
                                    .withStreamStates(
                                        streams.map { (namespace, name) ->
                                            AirbyteStreamState()
                                                .withStreamState(
                                                    JsonNodeFactory.instance
                                                        .objectNode()
                                                        .put(namespace, name)
                                                )
                                                .withStreamDescriptor(
                                                    StreamDescriptor()
                                                        .withNamespace(namespace)
                                                        .withName(name)
                                                )
                                        }
                                    )
                            )
                    )
            val expectedOutput =
                DestinationGlobalState(
                    sourceStats = DestinationStateMessage.Stats(recordCount = recordCount),
                    state = state,
                    streamStates =
                        streams.map { (namespace, name) ->
                            DestinationStateMessage.StreamState(
                                stream =
                                    DestinationStream(
                                        descriptor =
                                            DestinationStream.Descriptor(
                                                namespace = namespace,
                                                name = name
                                            )
                                    ),
                                state = JsonNodeFactory.instance.objectNode().put(namespace, name)
                            )
                        }
                )
            return Pair(input, expectedOutput)
        }
    }

    class TestDeserializationArgumentsProvider : ArgumentsProvider {
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            return Stream.of<Pair<AirbyteMessage, DestinationMessage>>().map { Arguments.of(it) }
        }
    }

    @Inject lateinit var deserializer: DefaultDestinationMessageDeserializer

    @ParameterizedTest
    @ArgumentsSource(TestDeserializationArgumentsProvider::class)
    fun testDeserialization(pair: Pair<AirbyteMessage, DestinationMessage>) {
        val (input, expectedOutput) = pair

        val serialized = Jsons.writeValueAsString(input)
        val actualOutput = deserializer.deserialize(serialized)

        Assertions.assertEquals(expectedOutput, actualOutput)
    }
}
