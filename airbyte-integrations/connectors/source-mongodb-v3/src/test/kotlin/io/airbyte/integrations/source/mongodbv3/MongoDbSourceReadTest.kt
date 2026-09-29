/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
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

    @Test
    fun testSnapshotResumesFromCheckpoint() {
        // Force a checkpoint every 2 records so the 3-document people collection needs two rounds.
        System.setProperty(MAX_RECORDS_PROPERTY, "2")
        try {
            val result: BufferingOutputConsumer = read(fullRefreshCatalog())
            Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
            val peopleState: MongoDbStreamStateValue = lastStreamStateFor(result, PEOPLE)
            Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, peopleState.status)
            Assertions.assertEquals("650000000000000000000003", peopleState.id)
            // An intermediate checkpoint at the 2nd _id proves the read resumed rather than
            // restarted.
            Assertions.assertTrue(
                allStreamStateIdsFor(result, PEOPLE).contains("650000000000000000000002"),
                "expected an intermediate checkpoint at the 2nd _id",
            )
        } finally {
            System.clearProperty(MAX_RECORDS_PROPERTY)
        }
    }

    @Test
    fun testWassSnapshotYieldsToCdcAndResumes() {
        // Negative budget => the incremental snapshot yields to CDC right after the first record.
        System.setProperty(MAX_SNAPSHOT_DURATION_PROPERTY, "-1")
        val sync1: BufferingOutputConsumer =
            try {
                read(incrementalCatalog())
            } finally {
                System.clearProperty(MAX_SNAPSHOT_DURATION_PROPERTY)
            }
        // It yielded before finishing: fewer than all 3 records and an IN_PROGRESS checkpoint.
        val readInSync1: Int = recordCountFor(sync1, PEOPLE)
        Assertions.assertTrue(readInSync1 in 1..2, "expected a partial snapshot, got $readInSync1")
        Assertions.assertEquals(
            MongoDbSnapshotStatus.IN_PROGRESS,
            lastStreamStateFor(sync1, PEOPLE).status,
        )

        // The next sync (no budget) resumes from the checkpoint and completes the snapshot.
        val sync2: BufferingOutputConsumer = read(incrementalCatalog(), sync1.states())
        Assertions.assertEquals(
            MongoDbSnapshotStatus.COMPLETE,
            lastStreamStateFor(sync2, PEOPLE).status,
        )
        Assertions.assertEquals(3, readInSync1 + recordCountFor(sync2, PEOPLE))
    }

    @Test
    fun testCdcCapturesInsertsUpdatesDeletes() {
        // Use a dedicated collection so mutations do not disturb the shared `people` snapshot
        // tests.
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(CDC)
            coll.drop()
            coll.insertMany(
                listOf(
                    Document("_id", ObjectId("660000000000000000000001")).append("name", "alice"),
                    Document("_id", ObjectId("660000000000000000000002")).append("name", "bob"),
                ),
            )
        }

        // Sync 1: cold-start snapshot; the Global feed captures a resume token before the snapshot.
        val sync1: BufferingOutputConsumer = read(incrementalCatalog(setOf(CDC)))
        Assertions.assertEquals(2, recordCountFor(sync1, CDC))
        val stateAfterSync1: List<AirbyteStateMessage> = sync1.states()

        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(CDC)
            coll.insertOne(
                Document("_id", ObjectId("660000000000000000000004")).append("name", "dave"),
            )
            coll.updateOne(
                Filters.eq("_id", ObjectId("660000000000000000000001")),
                Updates.set("age", 31),
            )
            coll.deleteOne(Filters.eq("_id", ObjectId("660000000000000000000002")))
        }

        // Sync 2: warm start resumes from the token and emits the 3 changes; no snapshot re-read.
        val sync2: BufferingOutputConsumer = read(incrementalCatalog(setOf(CDC)), stateAfterSync1)
        val changes: List<Map<String, Any?>> = recordDataFor(sync2, CDC)
        Assertions.assertEquals(3, changes.size, "expected insert + update + delete")
        Assertions.assertEquals(
            "dave",
            changes.first { it["_id"] == "660000000000000000000004" }["name"],
        )
        Assertions.assertEquals(
            31,
            changes.first { it["_id"] == "660000000000000000000001" }["age"],
        )
        Assertions.assertNotNull(
            changes.first { it["_id"] == "660000000000000000000002" }["_ab_cdc_deleted_at"],
            "a delete must set _ab_cdc_deleted_at",
        )
    }

    @Test
    fun testSyncModeMismatchWithSavedStateIsAConfigError() {
        // Saved as a completed FULL_REFRESH snapshot, but now configured INCREMENTAL.
        val state = globalState(peopleStatus = MongoDbSnapshotStatus.FULL_REFRESH)
        assertReadFails(
            incrementalCatalog(),
            state,
            "Stream $PEOPLE is INCREMENTAL but the saved status FULL_REFRESH doesn't match",
        )
    }

    @Test
    fun testSchemaModeMismatchWithSavedStateIsAConfigError() {
        // Config and catalog are schema-enforced, but the saved CDC state was captured schemaless.
        val state = globalState(MongoDbSnapshotStatus.COMPLETE, schemaEnforced = false)
        assertReadFails(
            incrementalCatalog(),
            state,
            "Mismatch between schema enforcing mode in sync configuration (true), catalog (true) " +
                "and saved state (false). Please reset your data.",
        )
    }

    @Test
    fun testInvalidResumeTokenFailsSyncByDefault() {
        val state = globalState(MongoDbSnapshotStatus.COMPLETE, resumeToken = BOGUS_RESUME_TOKEN)
        assertReadFails(incrementalCatalog(), state, "Saved offset is not valid")
    }

    @Test
    fun testInvalidResumeTokenResyncsWhenConfigured() {
        val resync =
            MongoDbSourceCheckTest.config(
                replicaSet.connectionString,
                listOf(TEST_DB),
                extraRootProperties =
                    mapOf("invalid_cdc_cursor_position_behavior" to "Re-sync data"),
            )
        val state = globalState(MongoDbSnapshotStatus.COMPLETE, resumeToken = BOGUS_RESUME_TOKEN)
        val result: BufferingOutputConsumer = read(incrementalCatalog(), state, resync)
        // State was reset, so the collection is re-snapshotted in full and a fresh token captured.
        Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
        Assertions.assertEquals(
            MongoDbSnapshotStatus.COMPLETE,
            lastStreamStateFor(result, PEOPLE).status,
        )
        val cdcState = result.states().mapNotNull { it.global?.sharedState }.last()
        val newToken = cdcState["resumeToken"]?.get("_data")?.asText()
        Assertions.assertNotNull(newToken, "expected a fresh resume token, got $cdcState")
        Assertions.assertNotEquals(BOGUS_RESUME_TOKEN, newToken)
    }

    private fun read(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = emptyList(),
        config: MongoDbSourceConfigurationSpecification = config(),
    ): BufferingOutputConsumer = CliRunner.source("read", config, catalog, state).run()

    /** Runs a read expected to fail and asserts the error trace contains [expectedMessage]. */
    private fun assertReadFails(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage>,
        expectedMessage: String,
    ) {
        val runnable: CliRunnable = CliRunner.source("read", config(), catalog, state)
        Assertions.assertThrows(ConnectorUncleanExitException::class.java) { runnable.run() }
        val errors: List<String> =
            runnable.results
                .traces()
                .filter { it.type == AirbyteTraceMessage.Type.ERROR }
                .map { it.error.message }
        Assertions.assertTrue(
            errors.any { it.contains(expectedMessage) },
            "expected an error containing '$expectedMessage', got $errors",
        )
    }

    /** A GLOBAL input state: one `people` stream state plus the CDC shared state. */
    private fun globalState(
        peopleStatus: MongoDbSnapshotStatus,
        schemaEnforced: Boolean = true,
        resumeToken: String? = null,
    ): List<AirbyteStateMessage> {
        val cdc =
            MongoDbCdcState(
                resumeToken = resumeToken?.let { Jsons.readTree("""{"_data":"$it"}""") },
                schemaEnforced = schemaEnforced,
            )
        val people =
            AirbyteStreamState()
                .withStreamDescriptor(StreamDescriptor().withName(PEOPLE).withNamespace(TEST_DB))
                .withStreamState(
                    MongoDbStreamStateValue.fromLastId(
                            ObjectId("650000000000000000000003"),
                            peopleStatus,
                        )
                        .toOpaqueStateValue(),
                )
        return listOf(
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(cdc.toOpaqueStateValue())
                        .withStreamStates(listOf(people)),
                ),
        )
    }

    private fun fullRefreshCatalog(): ConfiguredAirbyteCatalog =
        configuredCatalog(
            SyncMode.FULL_REFRESH,
            DestinationSyncMode.OVERWRITE,
            setOf(PEOPLE, EMPTY),
            includeEmpty = true,
        )

    private fun incrementalCatalog(names: Set<String> = setOf(PEOPLE)): ConfiguredAirbyteCatalog =
        configuredCatalog(
            SyncMode.INCREMENTAL,
            DestinationSyncMode.APPEND,
            names,
            includeEmpty = false
        )

    /** Builds a configured catalog from the connector's own discover output. */
    private fun configuredCatalog(
        syncMode: SyncMode,
        destinationSyncMode: DestinationSyncMode,
        names: Set<String>,
        includeEmpty: Boolean,
    ): ConfiguredAirbyteCatalog {
        val discovered = CliRunner.source("discover", config()).run().catalogs().first()
        val streams: List<ConfiguredAirbyteStream> =
            discovered.streams
                .filter { it.name in names }
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

    /**
     * All snapshot-checkpoint `_id`s emitted for a stream, in order, to observe resume progress.
     */
    private fun allStreamStateIdsFor(
        result: BufferingOutputConsumer,
        stream: String,
    ): List<String?> =
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
            .filter { it.streamState != null && !it.streamState.isNull }
            .mapNotNull {
                runCatching { MongoDbStreamStateValue.fromOpaqueStateValue(it.streamState).id }
                    .getOrNull()
            }

    companion object {
        const val TEST_DB = "test_db"
        const val PEOPLE = "people"
        const val EMPTY = "empty_coll"
        const val CDC = "cdc_coll"
        /**
         * A `_data` the server rejects (`FailedToParse`, not a hex string). Note that any
         * *well-formed* token is accepted and resumed from the oplog start, so a rejected token is
         * the only way to exercise the invalid-token path against a live replica set.
         */
        const val BOGUS_RESUME_TOKEN = "garbage"
        const val MAX_RECORDS_PROPERTY = "airbyte.connector.extract.mongodb.max-records-per-run"
        const val MAX_SNAPSHOT_DURATION_PROPERTY =
            "airbyte.connector.extract.mongodb.max-snapshot-duration-ms"

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
