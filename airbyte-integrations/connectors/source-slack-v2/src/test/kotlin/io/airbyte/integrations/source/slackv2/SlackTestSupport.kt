/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions

/** Helpers shared by the tests: configs against a [FakeSlackServer], in-process runs, results. */
object SlackTestSupport {

    /** 30 days before the first generated message. */
    val START_DATE: String =
        java.time.Instant.ofEpochSecond(FakeSlackData.EPOCH_START - 30 * 86400).toString()
    val START_EPOCH: Double = (FakeSlackData.EPOCH_START - 30 * 86400).toDouble()

    /** [server] documents which fake the config targets; the URL itself travels as a property. */
    @Suppress("UNUSED_PARAMETER")
    fun config(
        server: FakeSlackServer,
        token: String = FakeSlackData.TOKEN,
        oauth: Boolean = false,
        startDate: String = START_DATE,
        extra: Map<String, Any?> = emptyMap(),
    ): SlackSourceConfigurationSpecification {
        val json: ObjectNode =
            Jsons.objectNode().apply {
                put("start_date", startDate)
                put("lookback_window", 0)
                put("join_channels", true)
                set<JsonNode>(
                    "credentials",
                    if (oauth) {
                        Jsons.objectNode()
                            .put("option_title", CredentialsSpecification.OAUTH)
                            .put("client_id", "client")
                            .put("client_secret", "secret")
                            .put("access_token", token)
                    } else {
                        Jsons.objectNode()
                            .put("option_title", CredentialsSpecification.API_TOKEN)
                            .put("api_token", token)
                    },
                )
                extra.forEach { (k, v) -> set<JsonNode>(k, Jsons.valueToTree(v)) }
            }
        return Jsons.readValue(
            Jsons.writeValueAsString(json),
            SlackSourceConfigurationSpecification::class.java
        )
    }

    /** Points the connector at [server] and disables its client-side pacing for the run. */
    fun <T> withServer(
        server: FakeSlackServer,
        properties: Map<String, String> = emptyMap(),
        block: () -> T
    ): T {
        val all: Map<String, String> =
            mapOf(
                SlackSourceConfigurationFactory.API_BASE_URL_PROPERTY to server.baseUrl,
                SlackSharedState.RATE_LIMIT_SCALE_PROPERTY to "100000",
            ) + properties
        val previous: Map<String, String?> = all.keys.associateWith { System.getProperty(it) }
        all.forEach { (k, v) -> System.setProperty(k, v) }
        try {
            return block()
        } finally {
            previous.forEach { (k, v) ->
                if (v == null) System.clearProperty(k) else System.setProperty(k, v)
            }
        }
    }

    fun discover(
        server: FakeSlackServer,
        config: SlackSourceConfigurationSpecification = config(server)
    ): AirbyteCatalog =
        withServer(server) { CliRunner.source("discover", config).run().catalogs().single() }

    fun configured(
        catalog: AirbyteCatalog,
        name: String,
        syncMode: SyncMode
    ): ConfiguredAirbyteStream {
        val stream: AirbyteStream = catalog.streams.first { it.name == name }
        return ConfiguredAirbyteStream()
            .withStream(stream)
            .withSyncMode(syncMode)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(stream.defaultCursorField)
            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
    }

    fun catalog(vararg streams: ConfiguredAirbyteStream): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog().withStreams(streams.toList())

    fun streamState(name: String, json: String): AirbyteStateMessage =
        streamState(name, Jsons.readTree(json))

    fun streamState(name: String, json: JsonNode): AirbyteStateMessage =
        AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(StreamDescriptor().withName(name))
                    .withStreamState(json)
            )

    fun read(
        server: FakeSlackServer,
        catalog: ConfiguredAirbyteCatalog,
        config: SlackSourceConfigurationSpecification = config(server),
        state: List<AirbyteStateMessage>? = null,
        properties: Map<String, String> = emptyMap(),
    ): ReadResult =
        withServer(server, properties) {
            val runnable: CliRunnable = CliRunner.source("read", config, catalog, state)
            val failure: Throwable? =
                try {
                    runnable.run()
                    null
                } catch (e: Throwable) {
                    e
                }
            ReadResult(runnable.results, failure)
        }

    class ReadResult(val output: BufferingOutputConsumer, val failure: Throwable?) {
        val errors: List<String> =
            output
                .traces()
                .filter { it.type == AirbyteTraceMessage.Type.ERROR }
                .map { it.error.message ?: "" }

        fun assertNoErrors() {
            Assertions.assertTrue(errors.isEmpty(), "unexpected error traces: $errors")
            Assertions.assertNull(failure, "unexpected failure: $failure")
        }

        fun records(stream: String): List<JsonNode> =
            output.records().filter { it.stream == stream }.map(AirbyteRecordMessage::getData)

        fun statuses(stream: String): List<String> =
            output
                .traces()
                .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
                .filter { it.streamStatus.streamDescriptor.name == stream }
                .map { it.streamStatus.status.let(AirbyteStreamStatus::name) }

        fun stateMessages(stream: String): List<AirbyteStateMessage> =
            output.states().filter { it.stream?.streamDescriptor?.name == stream }

        fun states(stream: String): List<JsonNode> =
            stateMessages(stream).map { it.stream.streamState }

        fun lastState(stream: String): JsonNode = states(stream).last()
    }

    /** The records the connector should emit for a stream, computed from the workspace itself. */
    object Expected {
        fun channelMessages(
            workspace: FakeSlackWorkspace,
            channelId: String,
            oldest: Double,
            latest: Double
        ): List<ObjectNode> =
            (workspace.messages[channelId] ?: emptyList())
                .filter { m ->
                    val ts: String = m.get("ts").asText()
                    val threadTs: String? = m.get("thread_ts")?.asText()
                    threadTs == null ||
                        threadTs == ts ||
                        m.get("subtype")?.asText() == "thread_broadcast"
                }
                .filter { m -> m.get("ts").asText().toDouble() in oldest..latest }
                .map { decorate(it, channelId) }

        /**
         * What the legacy `threads` stream yields: for every history message, its thread (or
         * itself).
         */
        fun threads(
            workspace: FakeSlackWorkspace,
            channelId: String,
            oldest: Double,
            latest: Double,
            ignoreNoReplies: Boolean
        ): List<ObjectNode> {
            val all: List<ObjectNode> = workspace.messages[channelId] ?: emptyList()
            val result = ArrayList<ObjectNode>()
            val emittedThreads = HashSet<String>()
            for (m in channelMessages(workspace, channelId, oldest, latest)) {
                val ts: String = m.get("ts").asText()
                val threadTs: String? = m.get("thread_ts")?.asText()
                val replyCount: Int = m.get("reply_count")?.asInt() ?: 0
                val parentWithReplies: Boolean = threadTs == ts && replyCount > 0
                val broadcast: Boolean = threadTs != null && threadTs != ts
                if (!parentWithReplies && !broadcast) {
                    if (!ignoreNoReplies) result.add(m)
                    continue
                }
                if (broadcast && ignoreNoReplies) continue
                if (!emittedThreads.add(threadTs!!)) continue
                all.filter {
                        it.get("ts").asText() == threadTs ||
                            it.get("thread_ts")?.asText() == threadTs
                    }
                    .sortedBy { it.get("ts").asText().toDouble() }
                    .forEach { result.add(decorate(it, channelId)) }
            }
            return result
        }

        fun decorate(message: ObjectNode, channelId: String): ObjectNode =
            message.deepCopy().apply {
                set<JsonNode>("float_ts", SlackTs.floatTsNode(get("ts").asText()))
                put("channel_id", channelId)
            }
    }

    /** Multiset comparison of records on their canonical JSON. */
    fun assertSameRecords(expected: List<JsonNode>, actual: List<JsonNode>, label: String) {
        val e: Map<String, Int> =
            expected
                .map { Jsons.writeValueAsString(Jsons.readTree(Jsons.writeValueAsString(it))) }
                .groupingBy { it }
                .eachCount()
        val a: Map<String, Int> =
            actual
                .map { Jsons.writeValueAsString(Jsons.readTree(Jsons.writeValueAsString(it))) }
                .groupingBy { it }
                .eachCount()
        val missing: List<String> = e.filter { (k, v) -> (a[k] ?: 0) < v }.keys.take(3)
        val extra: List<String> = a.filter { (k, v) -> (e[k] ?: 0) < v }.keys.take(3)
        Assertions.assertEquals(
            expected.size,
            actual.size,
            "$label: record count; missing: $missing; extra: $extra"
        )
        Assertions.assertEquals(e, a, "$label: records differ; missing: $missing; extra: $extra")
    }
}
