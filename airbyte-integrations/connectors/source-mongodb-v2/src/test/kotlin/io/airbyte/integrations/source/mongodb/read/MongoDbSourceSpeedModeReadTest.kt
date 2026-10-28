/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.MongoDbTestConfigs
import io.airbyte.integrations.source.mongodb.SpeedModeTestSupport
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import java.math.BigDecimal
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicReference
import org.bson.Document
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * READ in speed mode: `DATA_CHANNEL_MEDIUM=SOCKET` with two Unix domain sockets, in `PROTOBUF` and
 * in `JSONL` format, for a cold start (snapshots) and a warm start (change events). The test plays
 * the destination: it connects to the socket files the connector creates, drains them while the
 * read runs and decodes the messages. The records must match, field by field, what the same read
 * produces on the STDIO channel (minus the sync-specific `_ab_cdc_updated_at` and `_ab_cdc_cursor`
 * of snapshot rows; the cursor must nevertheless be present on every socket record), and every
 * state message on the sockets must carry a `partition_id`.
 *
 * The data channel is configured through the Micronaut properties the platform's environment
 * variables map to (`airbyte.connector.data-channel.*`), set as JVM system properties for the
 * duration of the read; the class is [Isolated] because any connector context started meanwhile
 * would pick them up.
 */
@Isolated
class MongoDbSourceSpeedModeReadTest {

    @Test
    fun testProtobufOverSockets() {
        assertSpeedModeMatchesStdio(DataChannelFormat.PROTOBUF)
    }

    @Test
    fun testJsonlOverSockets() {
        assertSpeedModeMatchesStdio(DataChannelFormat.JSONL)
    }

    private fun assertSpeedModeMatchesStdio(format: DataChannelFormat) {
        resetChangeCollection()
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog()

        // Cold start: both streams are snapshotted; the Global feed only captures a token.
        val coldStdio: BufferingOutputConsumer = CliRunner.source("read", config(), catalog).run()
        val cold: SpeedModeRun = readInSpeedMode(format, catalog, state = emptyList())
        cold.assertMatches(coldStdio, expectedCounts = mapOf(PEOPLE to 3, CHANGES to 2))

        // Warm start from the STDIO cold run's state: only the three change events are emitted.
        applyChanges()
        val warmState: List<AirbyteStateMessage> = coldStdio.states()
        val warmStdio: BufferingOutputConsumer =
            CliRunner.source("read", config(), catalog, warmState).run()
        val warm: SpeedModeRun = readInSpeedMode(format, catalog, warmState)
        warm.assertMatches(warmStdio, expectedCounts = mapOf(CHANGES to 3))
        Assertions.assertTrue(
            warm.records.getValue(CHANGES).any { it["_ab_cdc_deleted_at"]?.isNull == false },
            "a delete must reach the sockets with _ab_cdc_deleted_at set",
        )
    }

    private fun readInSpeedMode(
        format: DataChannelFormat,
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage>,
    ): SpeedModeRun {
        // Unix domain socket paths are limited to about 100 bytes; /tmp keeps them short.
        val socketDir: Path =
            Files.createTempDirectory(
                Path.of("/tmp").takeIf { Files.isDirectory(it) }
                    ?: Path.of(System.getProperty("java.io.tmpdir")),
                "mongo-sockets-",
            )
        val socketPaths: List<Path> = (1..NUM_SOCKETS).map { socketDir.resolve("socket-$it.sock") }
        val readers: List<SpeedModeTestSupport.UnixSocketReader> = socketPaths.map {
            SpeedModeTestSupport.UnixSocketReader(it)
        }
        val properties: Map<String, String> =
            mapOf(
                "$DATA_CHANNEL_PROPERTY_PREFIX.medium" to "SOCKET",
                "$DATA_CHANNEL_PROPERTY_PREFIX.format" to format.name,
                "$DATA_CHANNEL_PROPERTY_PREFIX.socket-paths" to
                    socketPaths.joinToString(",") { it.toString() },
            )
        val cli: CliRunnable = CliRunner.source("read", config(), catalog, state)
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
                readers.forEach { it.poll() }
            }
        } finally {
            if (connector.isAlive) {
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
        return SpeedModeRun(format, catalog, cli.results, readers.map { it.bytes() })
    }

    /** What arrived over the sockets: records per stream, and the non-record protocol messages. */
    private inner class SpeedModeRun(
        val format: DataChannelFormat,
        val catalog: ConfiguredAirbyteCatalog,
        val stdout: BufferingOutputConsumer,
        socketBytes: List<ByteArray>,
    ) {
        val records: Map<String, List<ObjectNode>>
        val protocolMessages: List<JsonNode>

        init {
            when (format) {
                DataChannelFormat.PROTOBUF -> {
                    val messages: List<AirbyteMessageProtobuf> = socketBytes.flatMap {
                        SpeedModeTestSupport.parseProtobufMessages(it)
                    }
                    records =
                        messages
                            .filter { it.hasRecord() }
                            .map { it.record }
                            .groupBy({ it.streamName }) { decode(it) }
                    protocolMessages =
                        messages
                            .filter { it.hasAirbyteProtocolMessage() }
                            .map { Jsons.readTree(it.airbyteProtocolMessage) }
                }
                DataChannelFormat.JSONL -> {
                    val messages: List<JsonNode> = socketBytes.flatMap {
                        SpeedModeTestSupport.parseJsonlMessages(it)
                    }
                    records =
                        messages
                            .filter { it["type"].asText() == "RECORD" }
                            .map { it["record"] }
                            .onEach {
                                Assertions.assertTrue(
                                    it["partition_id"]?.asText()?.isNotBlank() == true,
                                    "partition_id of $it",
                                )
                            }
                            .groupBy({ it["stream"].asText() }) { it["data"] as ObjectNode }
                    protocolMessages = messages.filter { it["type"].asText() != "RECORD" }
                }
            }
        }

        /** Protobuf data slot of each field of a stream: the CDK orders the fields by name. */
        private fun slots(streamName: String): Map<String, Int> =
            catalog.streams
                .first { it.stream.name == streamName }
                .stream
                .jsonSchema["properties"]
                .fieldNames()
                .asSequence()
                .sorted()
                .mapIndexed { i, name -> name to i }
                .toMap()

        private fun decode(record: AirbyteRecordMessageProtobuf): ObjectNode {
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

        fun assertMatches(stdio: BufferingOutputConsumer, expectedCounts: Map<String, Int>) {
            val dump =
                "STDIO baseline:\n${stdio.dumpNonLogs()}\nspeed mode stdout:\n${stdout.dumpNonLogs()}"
            Assertions.assertEquals(
                expectedCounts.keys,
                records.keys,
                "streams with records\n$dump",
            )
            for ((stream, count) in expectedCounts) {
                val socketRecords: List<ObjectNode> = records.getValue(stream)
                Assertions.assertEquals(count, socketRecords.size, "records of $stream\n$dump")
                for (record in socketRecords) {
                    Assertions.assertTrue(
                        record["_ab_cdc_cursor"]?.isNull == false,
                        "_ab_cdc_cursor must be set over the sockets: $record",
                    )
                }
                val expected: List<String> =
                    stdio
                        .records()
                        .filter { it.stream == stream }
                        .map { comparable(it.data).toString() }
                        .sorted()
                Assertions.assertEquals(
                    expected,
                    socketRecords.map { comparable(it).toString() }.sorted(),
                    "records of $stream ($format)\n$dump",
                )
            }
            // States reach the destination over the sockets too, each tagged with the partition
            // whose records it covers.
            val socketStates: List<JsonNode> =
                protocolMessages.filter { it["type"]?.asText() == "STATE" }.map { it["state"] }
            Assertions.assertTrue(socketStates.isNotEmpty(), "no STATE over the sockets\n$dump")
            for (state in socketStates) {
                Assertions.assertTrue(
                    state["partition_id"]?.asText()?.isNotBlank() == true,
                    "partition_id of state $state",
                )
            }
        }

        /** A record minus the fields that legitimately differ between two runs. */
        private fun comparable(data: JsonNode): JsonNode =
            SpeedModeTestSupport.normalize(
                (data.deepCopy() as ObjectNode).apply {
                    remove("_ab_cdc_cursor")
                    remove("_ab_cdc_updated_at")
                },
            )
    }

    private fun incrementalCatalog(): ConfiguredAirbyteCatalog {
        val discovered = CliRunner.source("discover", config()).run().catalogs().first()
        return ConfiguredAirbyteCatalog()
            .withStreams(
                discovered.streams
                    .filter { it.name in setOf(PEOPLE, CHANGES) }
                    .map { stream ->
                        ConfiguredAirbyteStream()
                            .withStream(stream)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withCursorField(stream.defaultCursorField)
                            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
                    },
            )
    }

    private fun BufferingOutputConsumer.dumpNonLogs(): String =
        messages()
            .filter { it.type != AirbyteMessage.Type.LOG }
            .joinToString("\n") { Jsons.writeValueAsString(it) }

    companion object {
        const val TEST_DB = "speed_db"
        const val PEOPLE = "people"
        const val CHANGES = "changes"
        const val NUM_SOCKETS = 2
        val TIMEOUT: Duration = Duration.ofMinutes(3)

        lateinit var replicaSet: MongoDBContainer

        fun config(): MongoDbSourceConfigurationSpecification =
            MongoDbTestConfigs.config(replicaSet.connectionString, listOf(TEST_DB))

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDBContainer(DockerImageName.parse("mongo:7.0")).also { it.start() }
            MongoClients.create(replicaSet.connectionString).use { client: MongoClient ->
                client
                    .getDatabase(TEST_DB)
                    .getCollection(PEOPLE)
                    .insertMany(
                        listOf(
                            Document("_id", ObjectId("650000000000000000000001"))
                                .append("name", "alice")
                                .append("age", 30)
                                .append("active", true)
                                .append("tags", listOf("a", "b"))
                                .append("dec", Decimal128(BigDecimal("12.34")))
                                .append("joined", Date(1_700_000_000_000L))
                                .append("addr", Document("city", "Paris")),
                            Document("_id", ObjectId("650000000000000000000002"))
                                .append("name", "bob")
                                .append("age", 41)
                                .append("active", false)
                                .append("tags", emptyList<String>())
                                .append("dec", Decimal128(BigDecimal("0.1")))
                                .append("joined", Date(1_700_000_001_000L))
                                .append("addr", Document("city", "Rome")),
                            Document("_id", ObjectId("650000000000000000000003"))
                                .append("name", "carol")
                                .append("age", 25)
                                .append("active", true)
                                .append("tags", listOf("c"))
                                .append("dec", Decimal128(BigDecimal("7")))
                                .append("joined", Date(1_700_000_002_000L))
                                .append("addr", Document("city", "Oslo")),
                        ),
                    )
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }

        fun resetChangeCollection() {
            MongoClients.create(replicaSet.connectionString).use { client ->
                val coll = client.getDatabase(TEST_DB).getCollection(CHANGES)
                coll.drop()
                coll.insertMany(
                    listOf(
                        Document("_id", ObjectId("660000000000000000000001"))
                            .append("name", "alice")
                            .append("age", 30),
                        Document("_id", ObjectId("660000000000000000000002"))
                            .append("name", "bob")
                            .append("age", 41),
                    ),
                )
            }
        }

        fun applyChanges() {
            MongoClients.create(replicaSet.connectionString).use { client ->
                val coll = client.getDatabase(TEST_DB).getCollection(CHANGES)
                coll.insertOne(
                    Document("_id", ObjectId("660000000000000000000004"))
                        .append("name", "dave")
                        .append("age", 19),
                )
                coll.updateOne(
                    Filters.eq("_id", ObjectId("660000000000000000000001")),
                    Updates.set("age", 31),
                )
                coll.deleteOne(Filters.eq("_id", ObjectId("660000000000000000000002")))
            }
        }
    }
}
