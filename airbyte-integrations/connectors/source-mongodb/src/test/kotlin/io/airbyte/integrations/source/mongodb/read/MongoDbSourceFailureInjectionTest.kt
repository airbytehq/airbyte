/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.model.Filters
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.CHECKPOINT_INTERVAL_PROPERTY
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.CONNECTOR_APP_NAME
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.CUT_BLOCK_MILLIS
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.CUT_INTERVAL_MILLIS
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.assertFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.blocking
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.configuredCatalog
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.discover
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.failing
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.lastResumeTokenData
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.lastStreamState
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.read
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.readExpectingFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.records
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.skip
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.streamStates
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.times
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.withFailPoint
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.withFailingGetMore
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.withProperty
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.withSnapshotBatchSize
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import java.util.concurrent.CompletableFuture
import java.util.concurrent.TimeUnit
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.testcontainers.containers.MongoDBContainer

/**
 * What happens when the server fails or stalls *during* a READ, injected with MongoDB's
 * `failCommand` failpoint: a failure a retry recovers from ends the sync as a transient error with
 * a consistent checkpoint, the next sync resumes from it without losing a document, and a change
 * made while a snapshot runs is replayed by the next sync.
 */
class MongoDbSourceFailureInjectionTest {

    /**
     * The first round is cut after [BATCH] documents and checkpointed (its `getMore` held past the
     * checkpoint interval); the next round's `getMore` fails with a replica-set or cursor error
     * (the driver does not retry a `getMore`). A failing round is not checkpointed: the sync ends
     * transiently with the first round's checkpoint, and the next sync resumes after it, re-reading
     * what the failed round had emitted rather than losing anything.
     */
    @ParameterizedTest(name = "{1} ({0})")
    @CsvSource("10107, NotWritablePrimary", "43, CursorNotFound", "11600, InterruptedAtShutdown")
    fun testServerErrorMidSnapshotIsTransientAndResumesFromTheCheckpoint(
        code: Int,
        codeName: String,
    ) {
        val catalog: ConfiguredAirbyteCatalog = fullRefreshCatalog()
        val failed: BufferingOutputConsumer =
            withSnapshotBatchSize(BATCH) {
                withProperty(CHECKPOINT_INTERVAL_PROPERTY, CUT_INTERVAL_MILLIS.toString()) {
                    withFailPoint(
                        replicaSet,
                        times(1),
                        blocking("getMore", millis = CUT_BLOCK_MILLIS),
                    ) {
                        withFailingGetMore(replicaSet, skip(1), errorCode = code) {
                            readExpectingFailure(config(), catalog)
                        }
                    }
                }
            }
        assertFailure(failed, FailureType.TRANSIENT_ERROR, codeName)
        Assertions.assertEquals((1..2 * BATCH).toList(), ids(failed), "two rounds were emitted")
        val checkpoint = lastStreamState(failed, PEOPLE)
        Assertions.assertEquals(BATCH, checkpoint?.resumeIdValue(), "only round 1 is checkpointed")
        Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, checkpoint?.status)

        val resumed: BufferingOutputConsumer = read(config(), catalog, failed.states())
        Assertions.assertEquals((BATCH + 1..DOCUMENTS).toList(), ids(resumed))
    }

    /**
     * A connection the server closes mid-read is a transient error too; nothing of the failing
     * round is checkpointed, so the next sync reads the collection from the start.
     */
    @Test
    fun testClosedConnectionMidSnapshotIsTransient() {
        val catalog: ConfiguredAirbyteCatalog = fullRefreshCatalog()
        val failed: BufferingOutputConsumer =
            withSnapshotBatchSize(BATCH) {
                withFailPoint(
                    replicaSet,
                    times(1),
                    Document("failCommands", listOf("getMore")).append("closeConnection", true),
                ) {
                    readExpectingFailure(config(), catalog)
                }
            }
        assertFailure(failed, FailureType.TRANSIENT_ERROR, "")
        Assertions.assertEquals((1..BATCH).toList(), ids(failed))
        Assertions.assertNull(lastStreamState(failed, PEOPLE))
    }

    /** The change stream cannot be opened (election in progress): transient, no state change. */
    @Test
    fun testServerErrorOpeningTheChangeStreamIsTransient() {
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog()
        val sync1: BufferingOutputConsumer = read(config(), catalog)
        val token: String = checkNotNull(lastResumeTokenData(sync1))

        // The driver retries a failed `aggregate` once (retryable reads): fail both attempts.
        val failed: BufferingOutputConsumer =
            withFailPoint(replicaSet, times(2), failing("aggregate", errorCode = 10107)) {
                readExpectingFailure(config(), catalog, sync1.states())
            }
        assertFailure(failed, FailureType.TRANSIENT_ERROR, "NotWritablePrimary")
        Assertions.assertNull(lastResumeTokenData(failed), "no position is checkpointed")

        insert(1000)
        val resumed: BufferingOutputConsumer = read(config(), catalog, sync1.states())
        Assertions.assertEquals(listOf(1000), ids(resumed))
        Assertions.assertNotEquals(token, lastResumeTokenData(resumed))
    }

    /**
     * The stream fails after some events were read: the token is not advanced (it is checkpointed
     * once, when the read ends), so the next sync replays those events — never skips them.
     */
    @Test
    fun testServerErrorMidChangeStreamDoesNotAdvanceTheToken() {
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog()
        val sync1: BufferingOutputConsumer = read(config(), catalog)
        val token: String = checkNotNull(lastResumeTokenData(sync1))
        (1001..1003).forEach(::insert)

        val failed: BufferingOutputConsumer =
            withFailPoint(replicaSet, times(1), failing("getMore", errorCode = 10107)) {
                readExpectingFailure(config(), catalog, sync1.states())
            }
        assertFailure(failed, FailureType.TRANSIENT_ERROR, "NotWritablePrimary")
        Assertions.assertNull(lastResumeTokenData(failed))

        val resumed: BufferingOutputConsumer = read(config(), catalog, sync1.states())
        Assertions.assertEquals(listOf(1001, 1002, 1003), ids(resumed))
        Assertions.assertNotEquals(token, lastResumeTokenData(resumed))
    }

    /**
     * The server reports `ChangeStreamHistoryLost` (286) for the saved position — the real signal
     * that the oplog rolled past it, not a malformed token: "Fail sync" is a configuration error,
     * "Re-sync data" starts over with a new snapshot.
     */
    @Test
    fun testChangeStreamHistoryLostHonoursTheInvalidPositionSetting() {
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog()
        val sync1: BufferingOutputConsumer = read(config(), catalog)

        val failed: BufferingOutputConsumer =
            withFailPoint(replicaSet, times(1), failing("aggregate", errorCode = 286)) {
                readExpectingFailure(config(), catalog, sync1.states())
            }
        assertFailure(failed, FailureType.CONFIG_ERROR, "Saved offset is not valid")

        val resync: MongoDbSourceConfigurationSpecification =
            config(mapOf("invalid_cdc_cursor_position_behavior" to "Re-sync data"))
        val resynced: BufferingOutputConsumer =
            withFailPoint(replicaSet, times(1), failing("aggregate", errorCode = 286)) {
                read(resync, catalog, sync1.states())
            }
        Assertions.assertEquals(
            (1..DOCUMENTS).toList(),
            ids(resynced),
            "the snapshot is taken again",
        )
        Assertions.assertEquals(
            MongoDbSnapshotStatus.COMPLETE,
            lastStreamState(resynced, PEOPLE)?.status,
        )
    }

    /**
     * The change-stream position is captured before the snapshot starts, so a document inserted
     * while the snapshot is running is replayed by the next sync, after every snapshot row.
     */
    @Test
    fun testInsertDuringTheSnapshotIsReplayedByTheNextSync() {
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog()
        // The snapshot's `find` (the second `find` of the READ, after the `_id`-kind seek) is held
        // on the server; the insert happens while it is.
        val sync1: BufferingOutputConsumer =
            withFailPoint(replicaSet, skip(1), blocking("find", millis = 4000)) {
                val reading: CompletableFuture<BufferingOutputConsumer> =
                    CompletableFuture.supplyAsync {
                        read(config(), catalog)
                    }
                waitForConnectorOperation("find", PEOPLE)
                insert(1000)
                reading.get(2, TimeUnit.MINUTES)
            }
        Assertions.assertTrue(ids(sync1).count { it == 1000 } <= 1)

        val sync2: BufferingOutputConsumer = read(config(), catalog, sync1.states())
        val replayed = records(sync2, PEOPLE)
        Assertions.assertEquals(listOf(1000), replayed.map { it["_id"].asInt() })
        val snapshotCursors: List<Long> =
            records(sync1, PEOPLE).map { it["_ab_cdc_cursor"].asLong() }
        Assertions.assertTrue(
            replayed.single()["_ab_cdc_cursor"].asLong() > snapshotCursors.max(),
            "a change sorts above every snapshot row",
        )
    }

    /**
     * The CDK cancels a snapshot round that outlives the checkpoint target interval: the round's
     * last `_id` is checkpointed and the next round resumes after it, nothing lost or repeated. The
     * collection is bigger than one 16MB batch, so the chunk needs a `getMore`, which is held past
     * the interval.
     */
    @Test
    fun testCheckpointIntervalCancelsTheRoundAndTheNextOneResumesAfterTheLastId() {
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(BIG))
        System.setProperty(CHECKPOINT_INTERVAL_PROPERTY, "1500")
        val result: BufferingOutputConsumer =
            try {
                withFailPoint(replicaSet, times(1), blocking("getMore", millis = 4000)) {
                    read(config(), catalog)
                }
            } finally {
                System.clearProperty(CHECKPOINT_INTERVAL_PROPERTY)
            }
        Assertions.assertEquals(
            (1..BIG_DOCUMENTS).toList(),
            records(result, BIG).map { it["_id"].asInt() },
        )
        val firstCheckpoint: Int = streamStates(result, BIG).first().resumeIdValue() as Int
        Assertions.assertTrue(
            firstCheckpoint in 1 until BIG_DOCUMENTS,
            "the cancelled round checkpointed the last document it emitted: $firstCheckpoint",
        )
    }

    /** A collection whose sampling times out is left out; discovery still succeeds. */
    @Test
    fun testDiscoverKeepsThePartialResultWhenSamplingTimesOut() {
        val all: Set<String> = setOf(PEOPLE, ORDERS, BIG)
        val names: Set<String> =
            withFailPoint(replicaSet, times(1), failing("aggregate", errorCode = 50)) {
                discover(config()).streams.map { it.name }.toSet()
            }
        Assertions.assertEquals(all.size - 1, names.size, "one collection was dropped: $names")
        Assertions.assertTrue(names.all { it in all }, names.toString())
    }

    @AfterEach
    fun cleanUpInserts() {
        MongoClients.create(replicaSet.connectionString).use { client: MongoClient ->
            client
                .getDatabase(TEST_DB)
                .getCollection(PEOPLE)
                .deleteMany(Filters.gte("_id", FIRST_INSERTED_ID))
        }
    }

    private fun ids(result: BufferingOutputConsumer): List<Int> =
        records(result, PEOPLE).map { it["_id"].asInt() }

    private fun insert(id: Int) {
        MongoClients.create(replicaSet.connectionString).use { client: MongoClient ->
            client
                .getDatabase(TEST_DB)
                .getCollection(PEOPLE)
                .insertOne(Document("_id", id).append("v", id))
        }
    }

    /** Polls `$currentOp` until the connector's [command] on [collection] is running. */
    private fun waitForConnectorOperation(command: String, collection: String) {
        MongoClients.create(replicaSet.connectionString).use { client: MongoClient ->
            val deadline = System.currentTimeMillis() + 30_000
            while (System.currentTimeMillis() < deadline) {
                val running: Boolean =
                    client
                        .getDatabase("admin")
                        .aggregate(
                            listOf(
                                Document("\$currentOp", Document("allUsers", true)),
                                Document(
                                    "\$match",
                                    Document("appName", CONNECTOR_APP_NAME)
                                        .append(
                                            "\$or",
                                            listOf(
                                                // `{find: <collection>}`
                                                Document("command.$command", collection),
                                                // `{getMore: <cursor>, collection: <collection>}`
                                                Document(
                                                        "command.$command",
                                                        Document("\$exists", true),
                                                    )
                                                    .append("command.collection", collection),
                                            ),
                                        ),
                                ),
                            ),
                        )
                        .first() != null
                if (running) return
                Thread.sleep(100)
            }
            error("the connector's $command on $collection never showed up in \$currentOp")
        }
    }

    private fun config(
        extraRootProperties: Map<String, Any> = emptyMap(),
    ): MongoDbSourceConfigurationSpecification =
        MongoDbReadTestSupport.config(
            replicaSet,
            listOf(TEST_DB),
            extraRootProperties = extraRootProperties,
        )

    private fun fullRefreshCatalog(): ConfiguredAirbyteCatalog =
        configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(PEOPLE))

    private fun incrementalCatalog(): ConfiguredAirbyteCatalog =
        configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(PEOPLE))

    companion object {
        const val TEST_DB = "failpoint_db"
        const val PEOPLE = "people"
        const val ORDERS = "orders"
        const val DOCUMENTS = 300
        /** A collection whose documents do not fit one 16MB batch. */
        const val BIG = "big"
        const val BIG_DOCUMENTS = 300
        const val BIG_DOCUMENT_BYTES = 70_000
        /** Documents a test inserts have ids from here; they are removed after the test. */
        const val FIRST_INSERTED_ID = 1000
        const val BATCH = 100

        lateinit var replicaSet: MongoDBContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
            MongoClients.create(replicaSet.connectionString).use { client ->
                val db = client.getDatabase(TEST_DB)
                db.getCollection(PEOPLE)
                    .insertMany((1..DOCUMENTS).map { Document("_id", it).append("v", it) })
                db.getCollection(ORDERS).insertMany((1..5).map { Document("_id", it) })
                db.getCollection(BIG)
                    .insertMany(
                        (1..BIG_DOCUMENTS).map {
                            Document("_id", it).append("payload", "x".repeat(BIG_DOCUMENT_BYTES))
                        },
                    )
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }
    }
}
