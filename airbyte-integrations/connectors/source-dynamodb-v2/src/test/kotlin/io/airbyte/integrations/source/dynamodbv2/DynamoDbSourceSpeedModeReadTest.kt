/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

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
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.batchPutItems
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.createTableWithItems
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType

private val log = KotlinLogging.logger {}

/**
 * READ in speed mode against a seeded DynamoDB Local container: `DATA_CHANNEL_MEDIUM=SOCKET` with
 * two Unix domain sockets, in `PROTOBUF` and in `JSONL` format. The test plays the destination: it
 * connects to the socket files the connector creates, drains them while the read runs and decodes
 * the messages; the records must match, attribute by attribute, the records the same catalog
 * produces on the STDIO channel, every stream must end with a state on the sockets and a `COMPLETE`
 * status, and numbers must be plain on the wire.
 *
 * The data channel is configured through the Micronaut properties the platform's environment
 * variables map to (`airbyte.connector.data-channel.*`), set as JVM system properties for the
 * duration of the read; the class is [Isolated] because any connector context started meanwhile
 * would pick them up.
 */
@Isolated
class DynamoDbSourceSpeedModeReadTest {

    /**
     * Full refresh streams of the parity seed (`all_types` is sparse: its third item has two of the
     * fourteen attributes, which the protobuf channel must render as nulls, not as the previous
     * item's values) plus [EXOTIC_NUMBERS]; `many_items` is read incrementally from a saved cursor.
     */
    private val fullRefreshStreams: List<String> =
        listOf(
            "all_types",
            "composite_key",
            "numeric_key",
            "binary_key",
            "reserved_words",
            EXOTIC_NUMBERS,
            SPARSE,
        )
    private val streams: List<String> = fullRefreshStreams + INCREMENTAL_STREAM

    private fun defaultCatalog(namespace: String? = null): ConfiguredAirbyteCatalog =
        catalog(
            fullRefreshStreams.map {
                configured(it, SyncMode.FULL_REFRESH, namespace = namespace)
            } +
                configured(
                    INCREMENTAL_STREAM,
                    SyncMode.INCREMENTAL,
                    cursor = "v",
                    namespace = namespace
                )
        )

    private val defaultState: List<AirbyteStateMessage> =
        listOf(
            streamState(
                INCREMENTAL_STREAM,
                """{"cursor_field":["v"],"cursor":"600","cursor_record_count":1}""",
            )
        )

    @Test
    fun testProtobufOverSockets() {
        val run: SpeedModeRun =
            readInSpeedMode(DataChannelFormat.PROTOBUF, defaultCatalog(), defaultState)
        val messages: List<AirbyteMessageProtobuf> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseProtobufMessages(it) }
        Assertions.assertTrue(messages.any { it.hasRecord() }, run.dump())

        val protoRecords: List<AirbyteRecordMessageProtobuf> =
            messages.filter { it.hasRecord() }.map { it.record }
        val records: Map<String, List<JsonNode>> =
            protoRecords.groupBy({ it.streamName }) { record -> run.decode(record) }
        val protocolMessages: List<JsonNode> =
            messages
                .filter { it.hasAirbyteProtocolMessage() }
                .map { Jsons.readTree(it.airbyteProtocolMessage) }
        run.assertMatchesStdio(records, protocolMessages)

        // The wire values of the exotic numbers: typed, plain notation, exact digits.
        val exotic: AirbyteRecordMessageProtobuf =
            protoRecords.first {
                it.streamName == EXOTIC_NUMBERS && run.decode(it)["id"].asText() == "x1"
            }
        val slots: Map<String, Int> = run.slots(EXOTIC_NUMBERS)
        fun value(name: String): AirbyteValueProtobuf = exotic.getData(slots.getValue(name))
        fun text(name: String): String? = SpeedModeTestSupport.wireText(value(name))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.STRING, value("id").valueCase)
        // `n_exp` is `1e5` in item x1 and `7` in item x2; the last sampled item types the field as
        // an integer, and `1e5` is integral, so it travels as the exact integer 100000.
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, value("n_exp").valueCase)
        for (name in listOf("n_tiny", "n_big", "n_dec")) {
            Assertions.assertEquals(
                AirbyteValueProtobuf.ValueCase.BIG_DECIMAL,
                value(name).valueCase,
                name
            )
        }
        Assertions.assertEquals("100000", text("n_exp"))
        Assertions.assertEquals("-0.0000001", text("n_tiny"))
        Assertions.assertEquals("123456789012345678901234567890", text("n_big"))
        Assertions.assertEquals("12.34", text("n_dec"))
        Assertions.assertEquals(AirbyteValueProtobuf.ValueCase.JSON, value("nested").valueCase)
        Assertions.assertEquals(
            Jsons.readTree("""{"n":100000,"l":[25]}"""),
            Jsons.readTree(text("nested")!!),
        )
        // A number set is unordered: compare the elements as a set of plain decimals.
        Assertions.assertEquals(
            setOf("1000", "2.5"),
            Jsons.readTree(text("nset")!!)
                .map { it.decimalValue().stripTrailingZeros().toPlainString() }
                .toSet(),
        )
        for ((name, slot) in slots) {
            val wire: String = SpeedModeTestSupport.wireText(exotic.getData(slot)) ?: continue
            Assertions.assertFalse(
                SpeedModeTestSupport.SCIENTIFIC_NOTATION.containsMatchIn(wire),
                "$name is not plain on the wire: $wire",
            )
        }

        // A value of another type than the sampled schema declares (`flexible` is a string in
        // item 1 and a number in item 2, and the last sampled item wins): the JSONL channels send
        // the raw string, the protobuf slot is an integer and cannot hold it, so it is null with a
        // change record for the destination's `_airbyte_meta`.
        val item1: AirbyteRecordMessageProtobuf =
            protoRecords.first {
                it.streamName == "all_types" && run.decode(it)["id"].asText() == "1"
            }
        Assertions.assertEquals(
            Jsons.textNode("integer"),
            run.configured.properties("all_types")["flexible"]["airbyte_type"],
        )
        Assertions.assertTrue(run.decode(item1)["flexible"].isNull, run.decode(item1).toString())
        val change: AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange =
            item1.meta.changesList.single { it.field == "flexible" }
        Assertions.assertEquals(
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED,
            change.change,
        )
        Assertions.assertEquals(
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                .SOURCE_SERIALIZATION_ERROR,
            change.reason,
        )
        Assertions.assertEquals(
            "text",
            run.stdio
                .records()
                .first { it.stream == "all_types" && it.data["id"].asText() == "1" }
                .data["flexible"]
                .asText(),
        )
        // Item 2 holds the integer the schema declares.
        val item2: AirbyteRecordMessageProtobuf =
            protoRecords.first {
                it.streamName == "all_types" && run.decode(it)["id"].asText() == "2"
            }
        // JsonNode equality is class-sensitive (IntNode vs BigIntegerNode): compare the text.
        Assertions.assertEquals("100", run.decode(item2)["flexible"].asText())
        // Item 2 carries no change record: the CDK's protobuf consumer reuses one record builder
        // per stream and, since Bulk CDK 1.1.13, clears the previous record's meta changes.
        Assertions.assertEquals(
            0,
            item2.meta.changesCount,
            "item 2 inherited a change record from item 1: ${item2.meta}",
        )
    }

    @Test
    fun testJsonlOverSockets() {
        val run: SpeedModeRun =
            readInSpeedMode(DataChannelFormat.JSONL, defaultCatalog(), defaultState)
        val messages: List<JsonNode> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseJsonlMessages(it) }
        Assertions.assertTrue(messages.any { it["type"].asText() == "RECORD" }, run.dump())
        val records: Map<String, List<JsonNode>> =
            messages
                .filter { it["type"].asText() == "RECORD" }
                .map { it["record"] }
                .onEach {
                    Assertions.assertTrue(
                        it["partition_id"]?.asText()?.isNotBlank() == true,
                        "partition_id of $it",
                    )
                }
                .groupBy({ it["stream"].asText() }) { it["data"] }
        run.assertMatchesStdio(records, messages.filter { it["type"].asText() != "RECORD" })

        // The raw line of the exotic record: plain notation, exact digits.
        val line: String =
            run.socketBytes
                .flatMap { SpeedModeTestSupport.jsonlLines(it) }
                .single { it.contains("\"$EXOTIC_NUMBERS\"") && it.contains("\"x1\"") }
        Assertions.assertTrue(
            line.contains("\"n_exp\":100000,") || line.endsWith("\"n_exp\":100000}}"),
            line
        )
        Assertions.assertTrue(line.contains("\"n_tiny\":-0.0000001"), line)
        Assertions.assertTrue(line.contains("\"n_big\":123456789012345678901234567890"), line)
        Assertions.assertTrue(line.contains("\"n_dec\":12.34"), line)
        Assertions.assertFalse(SpeedModeTestSupport.SCIENTIFIC_NOTATION.containsMatchIn(line), line)
    }

    /** In speed mode, without a configured `concurrency`, one table is read per socket. */
    @Test
    fun testConcurrencyDefaultsToTheSocketCount() {
        val spec: DynamoDbSourceConfigurationSpecification = container.config()
        Assertions.assertEquals(
            2,
            DynamoDbSourceConfigurationFactory("SOCKET", listOf("/tmp/a.sock", "/tmp/b.sock"))
                .make(spec)
                .maxConcurrency,
        )
        Assertions.assertEquals(1, DynamoDbSourceConfigurationFactory().make(spec).maxConcurrency)
        // A configured value wins on either medium.
        val three: DynamoDbSourceConfigurationSpecification =
            container.config(extra = mapOf("concurrency" to 3))
        Assertions.assertEquals(
            3,
            DynamoDbSourceConfigurationFactory("SOCKET", listOf("/tmp/a.sock"))
                .make(three)
                .maxConcurrency,
        )
        Assertions.assertEquals(3, DynamoDbSourceConfigurationFactory().make(three).maxConcurrency)
    }

    /** A saved `ExclusiveStartKey` is honoured over sockets as on STDIO. */
    @Test
    fun testResumesFromASavedKeyOverSockets() {
        val catalog: ConfiguredAirbyteCatalog =
            catalog(listOf(configured(INCREMENTAL_STREAM, SyncMode.FULL_REFRESH)))
        val allIds: List<String> =
            CliRunner.source("read", container.config(), catalog).run().records().map {
                it.data["id"].asText()
            }
        Assertions.assertEquals(MANY_ITEMS, allIds.size)
        val run: SpeedModeRun =
            readInSpeedMode(
                DataChannelFormat.PROTOBUF,
                catalog,
                listOf(
                    streamState(
                        INCREMENTAL_STREAM,
                        """{"scan":{"exclusive_start_key":{"id":{"S":"${allIds[599]}"}}}}""",
                    )
                ),
            )
        val messages: List<AirbyteMessageProtobuf> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseProtobufMessages(it) }
        val ids: List<String> =
            messages.filter { it.hasRecord() }.map { run.decode(it.record)["id"].asText() }
        Assertions.assertEquals(allIds.subList(600, allIds.size), ids)
        val states: List<JsonNode> = run.socketStates(messages, INCREMENTAL_STREAM)
        Assertions.assertEquals(Jsons.readTree("""{"scan_complete":true}"""), states.last())
    }

    /**
     * One item per page and a 1 second checkpoint interval over a 2500-item table: the scan is
     * usually cut into several rounds (DynamoDB Local answers in well under a millisecond, so the
     * number of rounds depends on the machine). Every record must arrive exactly once, every
     * intermediate state must be a resumable key with a partition id, and the last state must mark
     * the scan complete.
     */
    @Test
    fun testCheckpointsOverSockets() {
        val catalog: ConfiguredAirbyteCatalog =
            catalog(listOf(configured(WIDE, SyncMode.FULL_REFRESH, stream = wideStream())))
        val run: SpeedModeRun =
            withScanPageLimit(1) {
                readInSpeedMode(
                    DataChannelFormat.PROTOBUF,
                    catalog,
                    state = null,
                    extraConfig = mapOf("checkpoint_target_interval_seconds" to 1),
                )
            }
        val messages: List<AirbyteMessageProtobuf> =
            run.socketBytes.flatMap { SpeedModeTestSupport.parseProtobufMessages(it) }
        val ids: List<String> =
            messages.filter { it.hasRecord() }.map { run.decode(it.record)["id"].asText() }
        Assertions.assertEquals(WIDE_ITEMS, ids.size)
        Assertions.assertEquals(WIDE_ITEMS, ids.toSet().size)
        val stateMessages: List<JsonNode> = run.socketStateMessages(messages, WIDE)
        log.info {
            "Checkpoints over sockets: ${stateMessages.size} state(s) for $WIDE_ITEMS items"
        }
        for (message in stateMessages) {
            Assertions.assertTrue(
                message["partition_id"]?.asText()?.isNotBlank() == true,
                message.toString()
            )
        }
        val states: List<JsonNode> = stateMessages.map { it["stream"]["stream_state"] }
        for (state in states.dropLast(1)) {
            val segment: JsonNode = state["scan"]["segments"].single()
            Assertions.assertTrue(segment["exclusive_start_key"].has("id"), state.toString())
        }
        Assertions.assertEquals(Jsons.readTree("""{"scan_complete":true}"""), states.last())
        Assertions.assertEquals(
            WIDE_ITEMS.toDouble(),
            stateMessages.sumOf { it["sourceStats"]["recordCount"].asDouble() },
        )
    }

    // ---------------------------------------------------------------- speed mode runner

    /** Runs the catalog once on STDIO (the baseline) and once over sockets. */
    private fun readInSpeedMode(
        format: DataChannelFormat,
        configured: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage>?,
        extraConfig: Map<String, Any?> = emptyMap(),
    ): SpeedModeRun {
        val config: DynamoDbSourceConfigurationSpecification = container.config(extra = extraConfig)
        val stdio: BufferingOutputConsumer =
            CliRunner.source("read", config, configured, state).run()

        // Unix domain socket paths are limited to about 100 bytes; /tmp keeps them short.
        val socketDir: Path =
            Files.createTempDirectory(
                Path.of("/tmp").takeIf { Files.isDirectory(it) }
                    ?: Path.of(System.getProperty("java.io.tmpdir")),
                "ddb-sockets-",
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
        val cli: CliRunnable = CliRunner.source("read", config, configured, state)
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
                        "read did not finish within $TIMEOUT",
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
            "the connector did not create every socket",
        )
        log.info {
            "Speed mode ($format): ${readers.map { it.bytes().size }} bytes received per socket, " +
                "${readers.sumOf { it.refusedConnections }} refused connection attempt(s)."
        }
        // Raw socket output, for debugging a failed assertion.
        val dumpDir: Path = Files.createDirectories(Path.of("build", "speed-mode"))
        readers.forEachIndexed { i, reader ->
            Files.write(dumpDir.resolve("${format.name.lowercase()}-socket-$i.bin"), reader.bytes())
        }
        return SpeedModeRun(format, configured, stdio, cli.results, readers.map { it.bytes() })
    }

    private inner class SpeedModeRun(
        val format: DataChannelFormat,
        val configured: ConfiguredAirbyteCatalog,
        val stdio: BufferingOutputConsumer,
        val speedModeStdout: BufferingOutputConsumer,
        val socketBytes: List<ByteArray>,
    ) {
        fun dump(): String =
            "STDIO baseline:\n${stdio.dumpNonLogs()}\nspeed mode stdout:\n${speedModeStdout.dumpNonLogs()}"

        /** Protobuf data slot of each attribute of a stream: the CDK orders the fields by name. */
        fun slots(streamName: String): Map<String, Int> =
            configured
                .properties(streamName)
                .fieldNames()
                .asSequence()
                .sorted()
                .mapIndexed { i, name -> name to i }
                .toMap()

        /** The `data` object of a protobuf record, as the JSONL channels would have emitted it. */
        fun decode(record: AirbyteRecordMessageProtobuf): ObjectNode {
            val slots: Map<String, Int> = slots(record.streamName)
            Assertions.assertEquals(slots.size, record.dataCount, "${record.streamName}: $record")
            Assertions.assertTrue(record.partitionId.isNotBlank(), "partition_id of $record")
            val data: ObjectNode = Jsons.objectNode()
            for ((name, slot) in slots) {
                data.set<JsonNode>(
                    name,
                    SpeedModeTestSupport.protobufValueToJson(record.getData(slot)),
                )
            }
            return data
        }

        /**
         * What the protobuf channel sends for a record the STDIO channel emitted: a value the
         * field's declared type cannot hold travels as null (with a change record), see
         * [DynamoDbPartitionReader]. The JSONL channels send the record as is.
         */
        fun asSentOverTheSockets(streamName: String, data: JsonNode): JsonNode {
            if (format != DataChannelFormat.PROTOBUF) return data
            val result: ObjectNode = data.deepCopy()
            for ((name, schema) in configured.properties(streamName).properties()) {
                val value: JsonNode = result[name] ?: continue
                val codec: DynamoDbJsonNodeCodec = DynamoDbFieldType.fromJsonSchema(schema).codec
                if (!codec.representable(value)) {
                    result.set<JsonNode>(name, Jsons.nullNode())
                }
            }
            return result
        }

        fun socketStateMessages(
            messages: List<AirbyteMessageProtobuf>,
            streamName: String
        ): List<JsonNode> =
            messages
                .filter { it.hasAirbyteProtocolMessage() }
                .map { Jsons.readTree(it.airbyteProtocolMessage) }
                .filter { it["type"]?.asText() == "STATE" }
                .map { it["state"] }
                .filter {
                    it["stream"]?.get("stream_descriptor")?.get("name")?.asText() == streamName
                }

        fun socketStates(
            messages: List<AirbyteMessageProtobuf>,
            streamName: String
        ): List<JsonNode> =
            socketStateMessages(messages, streamName).map { it["stream"]["stream_state"] }

        /**
         * [socketRecords] are the `data` objects received over the sockets, per stream;
         * [socketProtocolMessages] the non-record Airbyte messages received over the sockets.
         */
        fun assertMatchesStdio(
            socketRecords: Map<String, List<JsonNode>>,
            socketProtocolMessages: List<JsonNode>,
        ) {
            val expected: Map<String, List<JsonNode>> =
                stdio.records().groupBy({ it.stream }) {
                    SpeedModeTestSupport.normalize(asSentOverTheSockets(it.stream, it.data))
                }
            for (stream in streams) {
                Assertions.assertTrue(
                    expected[stream].orEmpty().isNotEmpty(),
                    "the STDIO baseline read nothing from $stream\n${dump()}",
                )
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
                streams.toSet(),
                socketRecords.keys,
                "streams with records over the sockets"
            )
            Assertions.assertEquals(3, socketRecords.getValue("all_types").size)
            Assertions.assertEquals(
                MANY_ITEMS - 600,
                socketRecords.getValue(INCREMENTAL_STREAM).size
            )

            // States are emitted to the destination over the sockets (and to the platform on
            // stdout); over the sockets they carry the partition id.
            val socketStateMessages: List<JsonNode> =
                socketProtocolMessages
                    .filter { it["type"]?.asText() == "STATE" }
                    .map { it["state"] }
            for (message in socketStateMessages) {
                Assertions.assertTrue(
                    message["partition_id"]?.asText()?.isNotBlank() == true,
                    "partition_id of state $message",
                )
            }
            val socketStates: Map<String, List<JsonNode>> =
                socketStateMessages
                    .filter { it["stream"] != null }
                    .groupBy({ it["stream"]["stream_descriptor"]["name"].asText() }) {
                        it["stream"]["stream_state"]
                    }
            Assertions.assertEquals(
                streams.toSet(),
                socketStates.keys,
                "streams with a STATE over the sockets\n${dump()}",
            )
            for (stream in fullRefreshStreams) {
                Assertions.assertEquals(
                    Jsons.readTree("""{"scan_complete":true}"""),
                    socketStates.getValue(stream).last(),
                    "final state of $stream",
                )
            }
            Assertions.assertEquals(
                Jsons.readTree(
                    """{"cursor_field":["v"],"cursor":"$MANY_ITEMS","cursor_record_count":1}"""
                ),
                socketStates.getValue(INCREMENTAL_STREAM).last(),
            )
            val stdoutStates: Set<String> =
                speedModeStdout.states().mapNotNull { it.stream?.streamDescriptor?.name }.toSet()
            Assertions.assertEquals(
                streams.toSet(),
                stdoutStates,
                "streams with a STATE on stdout\n${dump()}",
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
                    "statuses of $stream\n${dump()}",
                )
            }
            Assertions.assertTrue(
                speedModeStdout.traces().none { it.type == AirbyteTraceMessage.Type.ERROR },
                "error traces\n${dump()}",
            )
            // Two sockets, seven streams, concurrency 2 by default: both sockets carry data.
            Assertions.assertTrue(
                socketBytes.all { it.isNotEmpty() },
                "bytes per socket: ${socketBytes.map { it.size }}",
            )
        }
    }

    // ---------------------------------------------------------------- helpers

    private fun ConfiguredAirbyteCatalog.properties(streamName: String): ObjectNode =
        streams.first { it.stream.name == streamName }.stream.jsonSchema["properties"] as ObjectNode

    private fun configured(
        name: String,
        syncMode: SyncMode,
        cursor: String? = null,
        stream: AirbyteStream? = null,
        namespace: String? = null,
    ): ConfiguredAirbyteStream {
        val discovered: AirbyteStream =
            stream ?: discoveredCatalog.streams.first { it.name == name }
        // A copy: the discovered catalog is shared by the tests.
        val airbyteStream: AirbyteStream =
            Jsons.readValue(Jsons.writeValueAsString(discovered), AirbyteStream::class.java)
                .withNamespace(namespace)
        return ConfiguredAirbyteStream()
            .withStream(airbyteStream)
            .withSyncMode(syncMode)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(listOfNotNull(cursor))
            .withPrimaryKey(airbyteStream.sourceDefinedPrimaryKey)
    }

    private fun catalog(streams: List<ConfiguredAirbyteStream>): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog().withStreams(streams)

    private fun streamState(name: String, json: String): AirbyteStateMessage =
        AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(StreamDescriptor().withName(name))
                    .withStreamState(Jsons.readTree(json)),
            )

    /**
     * The `wide` table is created after discovery; its stream is declared here, in the legacy
     * `["null", <type>]` shapes on purpose: a catalog configured before the schemas became
     * canonical types its fields as JSONB and must still read over the sockets.
     */
    private fun wideStream(): AirbyteStream =
        AirbyteStream()
            .withName(WIDE)
            .withJsonSchema(
                Jsons.readTree(
                    """{"type":"object","properties":{"id":{"type":["null","string"]},
                        "filler":{"type":["null","string"]}}}"""
                )
            )
            .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(listOf(listOf("id")))

    /** Sets the scan page size (items per `Scan` request) for the connector runs in [block]. */
    private fun <T> withScanPageLimit(limit: Int, block: () -> T): T {
        System.setProperty(DynamoDbSharedState.SCAN_PAGE_LIMIT_PROPERTY, limit.toString())
        try {
            return block()
        } finally {
            System.clearProperty(DynamoDbSharedState.SCAN_PAGE_LIMIT_PROPERTY)
        }
    }

    private fun BufferingOutputConsumer.dumpNonLogs(): String =
        messages()
            .filter { it.type != AirbyteMessage.Type.LOG }
            .joinToString("\n") { Jsons.writeValueAsString(it) }

    companion object {
        const val NUM_SOCKETS = 2
        val TIMEOUT: Duration = Duration.ofMinutes(3)

        const val EXOTIC_NUMBERS = "exotic_numbers"
        const val SPARSE = "sparse"
        const val INCREMENTAL_STREAM = "many_items"
        const val MANY_ITEMS = 1200
        const val WIDE = "wide"
        const val WIDE_ITEMS = 2500

        lateinit var container: DynamoDbLocalContainer
        lateinit var client: DynamoDbClient
        lateinit var discoveredCatalog: AirbyteCatalog

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            container = DynamoDbLocalContainer().also { it.start() }
            client = container.client()
            DynamoDbParitySeed.seed(client)
            // Numbers whose BigDecimal.toString() is scientific notation, at every nesting level.
            client.createTableWithItems(
                EXOTIC_NUMBERS,
                listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                listOf(
                    DynamoDbJson.itemFromDynamoDbJson(
                        Jsons.readTree(
                            """{"id": {"S": "x1"}, "n_exp": {"N": "1e5"}, "n_tiny": {"N": "-0.0000001"},
                                "n_big": {"N": "123456789012345678901234567890"}, "n_dec": {"N": "12.34"},
                                "nested": {"M": {"n": {"N": "1e5"}, "l": {"L": [{"N": "2.5e1"}]}}},
                                "nset": {"NS": ["1e3", "2.5"]}}"""
                        )
                    ),
                    DynamoDbJson.itemFromDynamoDbJson(
                        Jsons.readTree("""{"id": {"S": "x2"}, "n_exp": {"N": "7"}}""")
                    ),
                ),
            )
            // Every item lacks an attribute every other item has: whatever the scan order, an
            // item follows one with an attribute it does not have, which must come out as null.
            client.createTableWithItems(
                SPARSE,
                listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                listOf(
                    mapOf(
                        "id" to AttributeValue.fromS("s1"),
                        "only_a" to AttributeValue.fromS("A")
                    ),
                    mapOf(
                        "id" to AttributeValue.fromS("s2"),
                        "only_b" to AttributeValue.fromS("B")
                    ),
                    mapOf(
                        "id" to AttributeValue.fromS("s3"),
                        "only_c" to AttributeValue.fromS("C")
                    ),
                ),
            )
            discoveredCatalog =
                CliRunner.source("discover", container.config()).run().catalogs().single()
            // Over 1 MB, so that a Scan without Limit needs several pages; created after discovery
            // so that it does not slow the sampling down.
            client.createTableWithItems(
                WIDE,
                listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                emptyList(),
            )
            val filler: String = "x".repeat(600)
            client.batchPutItems(
                WIDE,
                (1..WIDE_ITEMS).map {
                    mapOf(
                        "id" to AttributeValue.fromS("w-%04d".format(it)),
                        "filler" to AttributeValue.fromS(filler),
                    )
                },
            )
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            client.close()
            container.stop()
        }
    }
}
