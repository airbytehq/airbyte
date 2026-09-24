/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.sockets.FORMAT_PROPERTY
import io.airbyte.cdk.output.sockets.MEDIUM_PROPERTY
import io.airbyte.cdk.output.sockets.SOCKET_PATHS_PROPERTY
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated

private val log = KotlinLogging.logger {}

/**
 * READ in speed mode against the seeded emulator: `DATA_CHANNEL_MEDIUM=SOCKET` with two Unix domain
 * sockets, in `PROTOBUF` and in `JSONL` format. The test plays the destination: it connects to the
 * socket files the connector creates, drains them while the read runs and decodes the messages; the
 * records must match, column by column, the records the same catalog produces on the STDIO channel,
 * and every stream must end with a state on the sockets and a `COMPLETE` status.
 *
 * The data channel is configured through the Micronaut properties the platform's environment
 * variables map to (`airbyte.connector.data-channel.*`), set as JVM system properties for the
 * duration of the read; the class is [Isolated] because any connector context started meanwhile
 * would pick them up.
 */
@Isolated
class BigQuerySourceSpeedModeReadTest {

    private val config: BigQuerySourceConfigurationSpecification =
        BigQueryEmulatorTestFixture.config(datasetId = BigQueryEmulatorTestFixture.DATASET)

    private val streams: List<String> = listOf("all_types", "no_rows", "with_pk", "all_types_view")

    @Test
    fun testProtobufOverSockets() {
        val run: SpeedModeRun = readInSpeedMode(DataChannelFormat.PROTOBUF)
        val messages: List<AirbyteMessageProtobuf> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseProtobufMessages(it) }
        Assertions.assertTrue(messages.any { it.hasRecord() }, run.dump())

        val records: Map<String, List<JsonNode>> =
            messages
                .filter { it.hasRecord() }
                .map { it.record }
                .groupBy({ it.streamName }) { record ->
                    val schema: ObjectNode = run.configured.properties(record.streamName)
                    val fieldNames: List<String> =
                        schema.fieldNames().asSequence().sorted().toList()
                    Assertions.assertEquals(
                        fieldNames.size,
                        record.dataCount,
                        "${record.streamName}: $record"
                    )
                    val data: ObjectNode = Jsons.objectNode()
                    fieldNames.forEachIndexed { i, name ->
                        data.set<JsonNode>(
                            name,
                            SpeedModeTestSupport.protobufValueToJson(
                                SpeedModeTestSupport.decode(record.getData(i)),
                                schema[name]
                            )
                        )
                    }
                    Assertions.assertEquals(
                        BigQueryEmulatorTestFixture.DATASET,
                        record.streamNamespace
                    )
                    Assertions.assertTrue(
                        record.partitionId.isNotBlank(),
                        "partition_id of $record"
                    )
                    data
                }
        val protocolMessages: List<JsonNode> =
            messages
                .filter { it.hasAirbyteProtocolMessage() }
                .map { Jsons.readTree(it.airbyteProtocolMessage) }
        run.assertMatchesStdio(records, protocolMessages)
    }

    @Test
    fun testJsonlOverSockets() {
        val run: SpeedModeRun = readInSpeedMode(DataChannelFormat.JSONL)
        val messages: List<JsonNode> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseJsonlMessages(it) }
        Assertions.assertTrue(messages.any { it["type"].asText() == "RECORD" }, run.dump())
        val records: Map<String, List<JsonNode>> =
            messages
                .filter { it["type"].asText() == "RECORD" }
                .map { it["record"] }
                .onEach {
                    Assertions.assertEquals(
                        BigQueryEmulatorTestFixture.DATASET,
                        it["namespace"].asText()
                    )
                    Assertions.assertTrue(
                        it["partition_id"]?.asText()?.isNotBlank() == true,
                        "partition_id of $it"
                    )
                }
                .groupBy({ it["stream"].asText() }) { it["data"] }
        run.assertMatchesStdio(records, messages.filter { it["type"].asText() != "RECORD" })
    }

    /** Runs the configured catalog once on STDIO (the baseline) and once over sockets. */
    private fun readInSpeedMode(format: DataChannelFormat): SpeedModeRun {
        val catalog: AirbyteCatalog = CliRunner.source("discover", config).run().catalogs().single()
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    streams.map { configured(catalog.streams.first { s -> s.name == it }) }
                )
        val stdio: BufferingOutputConsumer = CliRunner.source("read", config, configured).run()

        // Unix domain socket paths are limited to about 100 bytes; /tmp keeps them short.
        val socketDir: Path =
            Files.createTempDirectory(
                Path.of("/tmp").takeIf { Files.isDirectory(it) }
                    ?: Path.of(System.getProperty("java.io.tmpdir")),
                "bq-sockets-"
            )
        val socketPaths: List<Path> = (1..NUM_SOCKETS).map { socketDir.resolve("socket-$it.sock") }
        val readers: List<SpeedModeTestSupport.UnixSocketReader> =
            socketPaths.map { SpeedModeTestSupport.UnixSocketReader(it) }
        val properties: Map<String, String> =
            mapOf(
                MEDIUM_PROPERTY to "SOCKET",
                FORMAT_PROPERTY to format.name,
                SOCKET_PATHS_PROPERTY to socketPaths.joinToString(",") { it.toString() },
            )
        val cli: CliRunnable = CliRunner.source("read", config, configured)
        val failure = AtomicReference<Throwable?>()
        val connector =
            Thread(
                {
                    try {
                        cli.run()
                    } catch (e: Throwable) {
                        failure.set(e)
                    }
                },
                "speed-mode-read",
            )
        try {
            SpeedModeTestSupport.withSystemProperties(properties) {
                connector.start()
                val deadline: Instant = Instant.now().plus(TIMEOUT)
                while (connector.isAlive) {
                    Assertions.assertTrue(
                        Instant.now().isBefore(deadline),
                        "read did not finish within $TIMEOUT"
                    )
                    readers.forEach { it.poll() }
                    Thread.sleep(20)
                }
                // Whatever was written just before the read finished is still in the kernel
                // buffers.
                readers.forEach { it.poll() }
            }
        } finally {
            if (connector.isAlive) {
                // Only reached when the test failed: do not leak a running read into other tests.
                connector.interrupt()
                connector.join(TIMEOUT.toMillis())
            }
            readers.forEach { runCatching { it.close() } }
            runCatching {
                socketPaths.forEach { Files.deleteIfExists(it) }
                Files.deleteIfExists(socketDir)
            }
        }
        failure.get()?.let {
            throw AssertionError("speed mode read failed: ${cli.results.dumpNonLogs()}", it)
        }
        Assertions.assertTrue(
            readers.all { it.isConnected },
            "the connector did not create every socket"
        )
        log.info {
            "Speed mode ($format): ${readers.map { it.bytes().size }} bytes received per socket, " +
                "${readers.sumOf { it.refusedConnections }} refused connection attempt(s)."
        }
        return SpeedModeRun(configured, stdio, cli.results, readers.map { it.bytes() })
    }

    private inner class SpeedModeRun(
        val configured: ConfiguredAirbyteCatalog,
        val stdio: BufferingOutputConsumer,
        val speedModeStdout: BufferingOutputConsumer,
        val socketBytes: List<ByteArray>,
    ) {
        fun dump(): String =
            "STDIO baseline:\n${stdio.dumpNonLogs()}\nspeed mode stdout:\n${speedModeStdout.dumpNonLogs()}"

        /**
         * [socketRecords] are the `data` objects received over the sockets, per stream;
         * [socketProtocolMessages] the non-record Airbyte messages received over the sockets.
         */
        fun assertMatchesStdio(
            socketRecords: Map<String, List<JsonNode>>,
            socketProtocolMessages: List<JsonNode>
        ) {
            val expected: Map<String, List<JsonNode>> =
                stdio.records().groupBy({ it.stream }) { SpeedModeTestSupport.normalize(it.data) }
            for (stream in streams) {
                Assertions.assertEquals(
                    expected[stream].orEmpty().map { it.toString() }.sorted(),
                    socketRecords[stream]
                        .orEmpty()
                        .map { SpeedModeTestSupport.normalize(it).toString() }
                        .sorted(),
                    "records of $stream\n${dump()}",
                )
            }
            Assertions.assertEquals(
                mapOf("all_types" to 2, "with_pk" to 3, "all_types_view" to 2),
                socketRecords.mapValues { it.value.size }
            )

            // States are emitted to the destination over the sockets (and to the platform on
            // stdout).
            val socketStates: Set<String> =
                socketProtocolMessages
                    .filter { it["type"]?.asText() == "STATE" }
                    .mapNotNull {
                        it["state"]?.get("stream")?.get("stream_descriptor")?.get("name")?.asText()
                    }
                    .toSet()
            Assertions.assertEquals(
                streams.toSet(),
                socketStates,
                "streams with a STATE over the sockets\n${dump()}"
            )
            val stdoutStates: Set<String> =
                speedModeStdout.states().mapNotNull { it.stream?.streamDescriptor?.name }.toSet()
            Assertions.assertEquals(
                streams.toSet(),
                stdoutStates,
                "streams with a STATE on stdout\n${dump()}"
            )

            // Stream statuses may travel on either channel; every stream must start and complete.
            val socketStatuses: List<Pair<String, String>> =
                socketProtocolMessages
                    .filter {
                        it["type"]?.asText() == "TRACE" &&
                            it["trace"]?.get("type")?.asText() == "STREAM_STATUS"
                    }
                    .map {
                        it["trace"]["stream_status"]["stream_descriptor"]["name"].asText() to
                            it["trace"]["stream_status"]["status"].asText()
                    }
            val stdoutStatuses: List<Pair<String, String>> =
                speedModeStdout
                    .traces()
                    .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
                    .map { it.streamStatus.streamDescriptor.name to it.streamStatus.status.name }
            for (stream in streams) {
                val statuses: Set<String> =
                    (socketStatuses + stdoutStatuses)
                        .filter { it.first == stream }
                        .map { it.second }
                        .toSet()
                Assertions.assertEquals(
                    setOf("STARTED", "COMPLETE"),
                    statuses,
                    "statuses of $stream\n${dump()}"
                )
            }
            Assertions.assertTrue(
                speedModeStdout.traces().none { it.type == AirbyteTraceMessage.Type.ERROR },
                "error traces\n${dump()}"
            )
        }
    }

    private fun ConfiguredAirbyteCatalog.properties(streamName: String): ObjectNode =
        streams.first { it.stream.name == streamName }.stream.jsonSchema["properties"] as ObjectNode

    private fun configured(stream: AirbyteStream): ConfiguredAirbyteStream =
        ConfiguredAirbyteStream()
            .withStream(stream)
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(emptyList())
            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)

    private fun BufferingOutputConsumer.dumpNonLogs(): String =
        messages()
            .filter { it.type != AirbyteMessage.Type.LOG }
            .joinToString("\n") { Jsons.writeValueAsString(it) }

    companion object {
        const val NUM_SOCKETS = 2
        val TIMEOUT: Duration = Duration.ofMinutes(3)

        @JvmStatic
        @BeforeAll
        fun startEmulator() {
            BigQueryEmulatorTestFixture.start()
        }
    }
}
