/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.math.BigDecimal
import org.bson.Document
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * Stage 3/4 (initial sync) gate: runs a full-refresh READ against a seeded replica set and checks
 * per-stream statuses, record counts, record content and the emitted per-stream checkpoint state.
 */
class MongoDbSourceReadTest {

    @Test
    fun testFullRefreshReadEmitsRecordsStatusesAndState() {
        val result: BufferingOutputConsumer = read(fullRefreshCatalog())

        // Every populated and empty collection is STARTED then COMPLETE, and never RUNNING.
        Assertions.assertEquals(
            setOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE),
            statusesFor(result, PEOPLE),
        )
        Assertions.assertEquals(
            setOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE),
            statusesFor(result, EMPTY),
        )
        Assertions.assertFalse(
            result.traces().any { it.streamStatus?.status == AirbyteStreamStatus.RUNNING },
        )

        Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
        Assertions.assertEquals(0, recordCountFor(result, EMPTY))

        // Record content: BSON values converted per the legacy shape.
        val alice: Map<String, Any?> = recordDataFor(result, PEOPLE).first { it["name"] == "alice" }
        Assertions.assertEquals("650000000000000000000001", alice["_id"])
        Assertions.assertEquals(30, alice["age"])
        Assertions.assertEquals(true, alice["active"])
        Assertions.assertEquals(listOf("a", "b"), alice["tags"])
        Assertions.assertEquals(12.34, (alice["dec"] as Number).toDouble())

        // A per-stream FULL_REFRESH checkpoint pointing at the last _id read.
        val peopleState: MongoDbStreamStateValue = lastStreamStateFor(result, PEOPLE)
        Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, peopleState.status)
        Assertions.assertEquals(MongoDbIdType.OBJECT_ID, peopleState.idType)
        Assertions.assertEquals("650000000000000000000003", peopleState.id)
    }

    @Test
    fun testIncrementalSnapshotEmitsCompleteState() {
        val result: BufferingOutputConsumer = read(incrementalCatalog())
        Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
        // An incremental stream's snapshot ends COMPLETE; the change stream (CDC) takes over later.
        val peopleState: MongoDbStreamStateValue = lastStreamStateFor(result, PEOPLE)
        Assertions.assertEquals(MongoDbSnapshotStatus.COMPLETE, peopleState.status)
        Assertions.assertEquals("650000000000000000000003", peopleState.id)
    }

    private fun read(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
    ): BufferingOutputConsumer = CliRunner.source("read", config(), catalog, state).run()

    private fun fullRefreshCatalog(): ConfiguredAirbyteCatalog =
        configuredCatalog(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE, includeEmpty = true)

    private fun incrementalCatalog(): ConfiguredAirbyteCatalog =
        configuredCatalog(SyncMode.INCREMENTAL, DestinationSyncMode.APPEND, includeEmpty = false)

    /** Builds a configured catalog from the connector's own discover output. */
    private fun configuredCatalog(
        syncMode: SyncMode,
        destinationSyncMode: DestinationSyncMode,
        includeEmpty: Boolean,
    ): ConfiguredAirbyteCatalog {
        val discovered = CliRunner.source("discover", config()).run().catalogs().first()
        val streams: List<ConfiguredAirbyteStream> =
            discovered.streams
                .filter { it.name == PEOPLE || it.name == EMPTY }
                .map { stream ->
                    ConfiguredAirbyteStream()
                        .withStream(stream)
                        .withSyncMode(syncMode)
                        .withDestinationSyncMode(destinationSyncMode)
                        .withCursorField(stream.defaultCursorField)
                        .withPrimaryKey(stream.sourceDefinedPrimaryKey)
                }
        // `empty_coll` is dropped from discover (no fields); add it back by hand to test statuses.
        val withEmpty: List<ConfiguredAirbyteStream> =
            if (!includeEmpty || streams.any { it.stream.name == EMPTY }) {
                streams
            } else {
                val emptyStream: AirbyteStream =
                    AirbyteStream()
                        .withName(EMPTY)
                        .withNamespace(TEST_DB)
                        .withJsonSchema(
                            Jsons.readTree(
                                """{"type":"object","properties":{"_id":{"type":"string"}}}""",
                            ),
                        )
                        .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                        .withSourceDefinedPrimaryKey(listOf(listOf("_id")))
                streams +
                    ConfiguredAirbyteStream()
                        .withStream(emptyStream)
                        .withSyncMode(syncMode)
                        .withDestinationSyncMode(destinationSyncMode)
                        .withPrimaryKey(listOf(listOf("_id")))
            }
        return ConfiguredAirbyteCatalog().withStreams(withEmpty)
    }

    private fun statusesFor(
        result: BufferingOutputConsumer,
        stream: String
    ): Set<AirbyteStreamStatus> =
        result
            .traces()
            .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
            .filter { it.streamStatus.streamDescriptor.name == stream }
            .map { it.streamStatus.status }
            .toSet()

    private fun recordCountFor(result: BufferingOutputConsumer, stream: String): Int =
        result.records().count { it.stream == stream }

    private fun recordDataFor(
        result: BufferingOutputConsumer,
        stream: String,
    ): List<Map<String, Any?>> =
        result
            .records()
            .filter { it.stream == stream }
            .map { record ->
                record.data.fields().asSequence().associate { (k, v) ->
                    k to
                        when {
                            v.isNull -> null
                            v.isBoolean -> v.asBoolean()
                            v.isIntegralNumber -> v.asInt()
                            v.isNumber -> v.asDouble()
                            v.isArray -> v.map { it.asText() }
                            v.isObject -> v
                            else -> v.asText()
                        }
                }
            }

    /**
     * MongoDB is a `global` source, so per-stream checkpoints are nested in GLOBAL state messages'
     * `streamStates` (older STREAM-typed messages are handled too for robustness).
     */
    private fun lastStreamStateFor(
        result: BufferingOutputConsumer,
        stream: String,
    ): MongoDbStreamStateValue {
        val streamState =
            result
                .states()
                .flatMap { message ->
                    when {
                        message.global != null -> message.global.streamStates
                        message.stream != null -> listOf(message.stream)
                        else -> emptyList()
                    }
                }
                .filter { it.streamDescriptor.name == stream }
                .last { it.streamState != null && !it.streamState.isNull }
        return MongoDbStreamStateValue.fromOpaqueStateValue(streamState.streamState)
    }

    companion object {
        const val TEST_DB = "test_db"
        const val PEOPLE = "people"
        const val EMPTY = "empty_coll"

        lateinit var replicaSet: MongoDBContainer

        fun config(): MongoDbSourceConfigurationSpecification =
            MongoDbSourceCheckTest.config(replicaSet.connectionString, listOf(TEST_DB))

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDBContainer(DockerImageName.parse("mongo:7.0")).also { it.start() }
            MongoClients.create(replicaSet.connectionString).use(::seed)
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }

        fun seed(client: MongoClient) {
            val db = client.getDatabase(TEST_DB)
            db.getCollection(PEOPLE)
                .insertMany(
                    listOf(
                        Document("_id", ObjectId("650000000000000000000001"))
                            .append("name", "alice")
                            .append("age", 30)
                            .append("active", true)
                            .append("tags", listOf("a", "b"))
                            .append("dec", Decimal128(BigDecimal("12.34"))),
                        Document("_id", ObjectId("650000000000000000000002"))
                            .append("name", "bob")
                            .append("age", 41)
                            .append("active", false)
                            .append("tags", emptyList<String>())
                            .append("dec", Decimal128(BigDecimal("0.1"))),
                        Document("_id", ObjectId("650000000000000000000003"))
                            .append("name", "carol"),
                    ),
                )
            db.createCollection(EMPTY)
        }
    }
}
