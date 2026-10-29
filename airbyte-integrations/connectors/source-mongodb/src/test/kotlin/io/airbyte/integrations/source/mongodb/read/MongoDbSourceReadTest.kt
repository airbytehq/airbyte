/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.model.ChangeStreamPreAndPostImagesOptions
import com.mongodb.client.model.CreateCollectionOptions
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import io.airbyte.integrations.source.mongodb.MongoDbTestConfigs
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbResumeTokens
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdType
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdTypes
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
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
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import org.bson.BinaryVector
import org.bson.BsonArray
import org.bson.BsonBinary
import org.bson.BsonBinarySubType
import org.bson.BsonBoolean
import org.bson.BsonDateTime
import org.bson.BsonDbPointer
import org.bson.BsonDecimal128
import org.bson.BsonDocument
import org.bson.BsonDouble
import org.bson.BsonInt32
import org.bson.BsonInt64
import org.bson.BsonJavaScript
import org.bson.BsonJavaScriptWithScope
import org.bson.BsonMaxKey
import org.bson.BsonMinKey
import org.bson.BsonNull
import org.bson.BsonObjectId
import org.bson.BsonRegularExpression
import org.bson.BsonString
import org.bson.BsonSymbol
import org.bson.BsonTimestamp
import org.bson.BsonUndefined
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Code
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer

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

        // A per-stream FULL_REFRESH checkpoint; finished, so with no _id: the next sync starts
        // over (an interrupted one keeps its last _id so a retry resumes).
        val peopleState: MongoDbStreamStateValue = lastStreamStateFor(result, PEOPLE)
        Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, peopleState.status)
        Assertions.assertNull(peopleState.id)
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
        // The first round is cut after 2 of the 3 people, so a second round resumes after them.
        val result: BufferingOutputConsumer = readCutAfter(2, fullRefreshCatalog())
        Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
        val peopleState: MongoDbStreamStateValue = lastStreamStateFor(result, PEOPLE)
        Assertions.assertEquals(MongoDbSnapshotStatus.FULL_REFRESH, peopleState.status)
        Assertions.assertNull(peopleState.id, "finished: start over next sync")
        // An intermediate checkpoint at the 2nd _id proves the read resumed rather than restarted.
        Assertions.assertTrue(
            allStreamStateIdsFor(result, PEOPLE).contains("650000000000000000000002"),
            "expected an intermediate checkpoint at the 2nd _id",
        )
    }

    @Test
    fun testWassSnapshotYieldsToCdcAndResumes() {
        // A zero-hour budget (the spec's minimum of 4 is enforced by the platform, not the
        // connector) => the incremental snapshot yields to CDC right after its first record. The
        // sync then ends with a transient error, its progress checkpointed, so the platform
        // retries immediately and the retry drains the change stream before resuming.
        val expiredBudget: MongoDbSourceConfigurationSpecification =
            config().apply { initialLoadTimeoutHours = 0 }
        val sync1: BufferingOutputConsumer = run {
            val runnable: CliRunnable =
                CliRunner.source("read", expiredBudget, incrementalCatalog())
            Assertions.assertThrows(ConnectorUncleanExitException::class.java) { runnable.run() }
            val errors: List<AirbyteTraceMessage> =
                runnable.results.traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }
            Assertions.assertTrue(
                errors.any {
                    it.error.failureType == AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR &&
                        it.error.message.contains("initial_load_timeout_hours")
                },
                "expected a transient initial-load error, got ${errors.map { it.error.message }}",
            )
            runnable.results
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
        // `_ab_cdc_cursor` is a MongoDB oplog time: the event's own time on a change, the time of
        // the change-stream position the sync saved on a snapshot row. Every event a later sync
        // replays is strictly after that position, so a change always sorts above the snapshot
        // row it supersedes — whichever node served the snapshot, and across syncs, since the
        // times come from the server rather than the (fixed) test clock.
        val cursors: List<Long> =
            sync2.records().filter { it.stream == CDC }.map { it.data["_ab_cdc_cursor"].asLong() }
        Assertions.assertEquals(3, cursors.size)
        Assertions.assertEquals(cursors.sorted(), cursors)
        Assertions.assertEquals(cursors.toSet().size, cursors.size, "cursors must be distinct")
        val snapshotCursors: Set<Long> =
            sync1
                .records()
                .filter { it.stream == CDC }
                .map { it.data["_ab_cdc_cursor"].asLong() }
                .toSet()
        val cdcState: MongoDbCdcState =
            MongoDbCdcState.fromOpaqueStateValue(
                stateAfterSync1.mapNotNull { it.global?.sharedState }.last(),
            )!!
        val savedPosition: BsonTimestamp =
            MongoDbResumeTokens.timestamp(cdcState.resumeTokenBson()!!)
        // The state records the saved position's time, and the snapshot rows carry it (to the
        // second, which is enough: every later change is strictly past the position).
        Assertions.assertEquals(
            Instant.ofEpochSecond(savedPosition.time.toLong()),
            cdcState.cdcSyncedUntil,
        )
        Assertions.assertEquals(
            setOf(BsonTimestamp(savedPosition.time, 0).value),
            snapshotCursors,
            "snapshot rows carry the saved position",
        )
        Assertions.assertTrue(
            cursors.first() > savedPosition.value,
            "changes must sort above the snapshot rows: $cursors vs $savedPosition",
        )
    }

    /**
     * With pre-images stored on the collection, a delete record carries the deleted document (not
     * just its `_id`), and an update whose document is already gone by the time of the lookup is
     * emitted as a delete rather than dropped — both as the legacy connector behaved.
     */
    @Test
    fun testDeletesCarryPreImageAndUpdateOfDeletedDocumentIsADelete() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val db = client.getDatabase(TEST_DB)
            db.getCollection(PRE_IMAGE_CDC).drop()
            db.createCollection(
                PRE_IMAGE_CDC,
                CreateCollectionOptions()
                    .changeStreamPreAndPostImagesOptions(ChangeStreamPreAndPostImagesOptions(true)),
            )
            db.getCollection(PRE_IMAGE_CDC)
                .insertMany(
                    listOf(
                        Document("_id", 1).append("name", "alice").append("age", 30),
                        Document("_id", 2).append("name", "bob").append("age", 41),
                    ),
                )
        }
        // Built before the deletes: an emptied collection is no longer discovered.
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog(setOf(PRE_IMAGE_CDC))
        val sync1: BufferingOutputConsumer = read(catalog)
        Assertions.assertEquals(2, recordCountFor(sync1, PRE_IMAGE_CDC))

        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(PRE_IMAGE_CDC)
            // Update then delete before the connector can look the document up.
            coll.updateOne(Filters.eq("_id", 1), Updates.set("age", 31))
            coll.deleteOne(Filters.eq("_id", 1))
            coll.deleteOne(Filters.eq("_id", 2))
        }
        val sync2: BufferingOutputConsumer = read(catalog, sync1.states())
        val changes: List<Map<String, Any?>> = recordDataFor(sync2, PRE_IMAGE_CDC)
        Assertions.assertEquals(3, changes.size, "update-of-deleted + 2 deletes: $changes")
        Assertions.assertTrue(
            changes.all { it["_ab_cdc_deleted_at"] != null },
            "every change must be a delete: $changes",
        )
        // Pre-images: the deleted documents' fields travel with the delete.
        Assertions.assertEquals(
            listOf("alice", "alice", "bob"),
            changes.map { it["name"] }.sortedBy { it.toString() },
        )
        val bob: Map<String, Any?> = changes.first { it["_id"] == 2 }
        Assertions.assertEquals(41, bob["age"])
    }

    /**
     * A busy cluster never lets `tryNext()` come back empty. The read must still end: it stops
     * after the first event past the cluster time captured when the read started, checkpoints the
     * token of the last emitted event, and the next sync picks up the rest without loss or repeat.
     */
    @Test
    fun testCdcStopsAtTargetUnderContinuousWrites() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(BUSY_CDC)
            coll.drop()
            coll.insertOne(Document("_id", 0).append("seq", 0))
        }
        val sync1: BufferingOutputConsumer = read(incrementalCatalog(setOf(BUSY_CDC)))
        Assertions.assertEquals(1, recordCountFor(sync1, BUSY_CDC))

        val inserted = AtomicInteger(0)
        val writing = AtomicBoolean(true)
        val writer = Thread {
            MongoClients.create(replicaSet.connectionString).use { client ->
                val coll = client.getDatabase(TEST_DB).getCollection(BUSY_CDC)
                while (writing.get()) {
                    val seq: Int = inserted.incrementAndGet()
                    coll.insertOne(Document("_id", seq).append("seq", seq))
                }
            }
        }
        writer.start()
        try {
            Thread.sleep(500) // changes are already flowing when the read starts
            val sync2: BufferingOutputConsumer =
                read(incrementalCatalog(setOf(BUSY_CDC)), sync1.states())
            Assertions.assertTrue(recordCountFor(sync2, BUSY_CDC) > 0, "expected changes in sync 2")
            Assertions.assertTrue(
                writing.get() && writer.isAlive,
                "the writer must still be running when the read returns",
            )
            writing.set(false)
            writer.join()

            val sync3: BufferingOutputConsumer =
                read(incrementalCatalog(setOf(BUSY_CDC)), sync2.states())
            val seen: List<Int> =
                (recordDataFor(sync2, BUSY_CDC) + recordDataFor(sync3, BUSY_CDC)).map {
                    it["_id"] as Int
                }
            Assertions.assertEquals(seen.toSet().size, seen.size, "no change may be emitted twice")
            Assertions.assertEquals(
                (1..inserted.get()).toSet(),
                seen.toSet(),
                "no change may be lost",
            )
        } finally {
            writing.set(false)
            writer.join()
        }
    }

    /** Without an incremental stream there is nothing to read from the change stream. */
    @Test
    fun testFullRefreshOnlyCatalogDoesNotReadTheChangeStream() {
        val result: BufferingOutputConsumer = read(fullRefreshCatalog())
        Assertions.assertEquals(3, recordCountFor(result, PEOPLE))
        val shared: List<JsonNode> = result.states().mapNotNull { it.global?.sharedState }
        Assertions.assertTrue(
            shared.none { it.hasNonNull("resumeToken") },
            "a full-refresh-only sync must not capture a resume token, got $shared",
        )
    }

    /**
     * An `_id` kind without a dedicated encoding (here JavaScript code; MongoDB itself forbids
     * array, regex and undefined `_id`s) is checkpointed as typed extended JSON, so the resume
     * filter `_id > <code>` matches the right BSON type and the collection resumes mid-way like any
     * other.
     */
    @Test
    fun testOtherIdKindsResumeMidSnapshot() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(CODE_ID)
            coll.drop()
            coll.insertMany(
                listOf("a", "b", "c").map {
                    Document("_id", Code("function $it() {}")).append("v", it)
                },
            )
        }
        val result: BufferingOutputConsumer =
            readCutAfter(2, incrementalCatalog(setOf(CODE_ID)), cursors = 2)
        Assertions.assertEquals(
            listOf("a", "b", "c"),
            recordDataFor(result, CODE_ID).map { it["v"] as String },
        )
        val checkpoints: List<MongoDbStreamStateValue> = allStreamStatesFor(result, CODE_ID)
        Assertions.assertEquals(MongoDbIdType.BSON, checkpoints.first().idType)
        Assertions.assertEquals(
            BsonJavaScript("function b() {}"),
            checkpoints.first().resumeIdValue(),
        )
        Assertions.assertEquals(MongoDbSnapshotStatus.COMPLETE, checkpoints.last().status)
    }

    /**
     * A snapshot resumed after a checkpoint that no document follows anymore (deleted since) reads
     * nothing: that round is what completes the snapshot, keeping the checkpoint's `_id`.
     */
    @Test
    fun testResumedRoundWithNothingLeftCompletes() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(NOTHING_LEFT)
            coll.drop()
            coll.insertMany((1..3).map { Document("_id", it).append("v", it) })
        }
        val catalog: ConfiguredAirbyteCatalog = incrementalCatalog(setOf(NOTHING_LEFT))
        // An expired WASS budget: the first sync yields right after its first record.
        val yielded: BufferingOutputConsumer = run {
            val runnable: CliRunnable =
                CliRunner.source("read", config().apply { initialLoadTimeoutHours = 0 }, catalog)
            Assertions.assertThrows(ConnectorUncleanExitException::class.java) { runnable.run() }
            runnable.results
        }
        val read: Int = recordCountFor(yielded, NOTHING_LEFT)
        Assertions.assertTrue(read in 1..2, "yielded after its first record(s): $read")
        val checkpoint: MongoDbStreamStateValue = lastStreamStateFor(yielded, NOTHING_LEFT)
        Assertions.assertEquals(MongoDbSnapshotStatus.IN_PROGRESS, checkpoint.status)
        Assertions.assertEquals(read, checkpoint.resumeIdValue())

        MongoClients.create(replicaSet.connectionString).use { client ->
            client
                .getDatabase(TEST_DB)
                .getCollection(NOTHING_LEFT)
                .deleteMany(Filters.gt("_id", read))
        }
        val resumed: BufferingOutputConsumer = read(catalog, yielded.states())
        // The deletions come back through the change stream; the snapshot itself emits nothing.
        Assertions.assertTrue(
            recordDataFor(resumed, NOTHING_LEFT).all { it["_ab_cdc_deleted_at"] != null },
            "no snapshot row: ${recordDataFor(resumed, NOTHING_LEFT)}",
        )
        val completed: MongoDbStreamStateValue = lastStreamStateFor(resumed, NOTHING_LEFT)
        Assertions.assertEquals(MongoDbSnapshotStatus.COMPLETE, completed.status)
        Assertions.assertEquals(read, completed.resumeIdValue())
    }

    @Test
    fun testDocumentIdCollectionResumesMidSnapshot() {
        // v2 2.1.0: `_id` values that are embedded documents are supported. The first round is cut
        // after 2 of 3 documents so the resume filter `_id > <document>` runs against the server.
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(DOC_ID)
            coll.drop()
            coll.insertMany(
                (1..3).map { n ->
                    Document("_id", Document("tenant", "acme").append("seq", n.toLong()))
                        .append("v", n)
                },
            )
        }
        val result: BufferingOutputConsumer =
            readCutAfter(
                2,
                configuredCatalog(
                    SyncMode.FULL_REFRESH,
                    DestinationSyncMode.OVERWRITE,
                    setOf(DOC_ID),
                    includeEmpty = false,
                ),
            )
        val records = result.records().filter { it.stream == DOC_ID }
        Assertions.assertEquals(3, records.size)
        Assertions.assertEquals(listOf(1, 2, 3), records.map { it.data["v"].asInt() })
        Assertions.assertEquals(listOf(1L, 2L, 3L), records.map { it.data["_id"]["seq"].asLong() })
        // The mid-collection checkpoint (after 2 of 3): a document `_id` as extended JSON.
        val state: MongoDbStreamStateValue = allStreamStatesFor(result, DOC_ID).first()
        Assertions.assertEquals(MongoDbIdType.OBJECT, state.idType)
        Assertions.assertTrue(state.id!!.contains("\"seq\""), state.id)
    }

    /**
     * Every dedicated `_id` encoding checkpoints mid-collection and resumes without loss or
     * repeats.
     */
    @Test
    fun testTypedIdCollectionsResumeMidSnapshot() {
        val collections: Map<String, Pair<List<Any>, MongoDbIdType>> =
            mapOf(
                STRING_ID to Pair(listOf("id-1", "id-2", "id-3"), MongoDbIdType.STRING),
                INT_ID to Pair(listOf(1, 2, 3), MongoDbIdType.INT),
                LONG_ID to
                    Pair(
                        listOf(10_000_000_000L, 10_000_000_001L, 10_000_000_002L),
                        MongoDbIdType.LONG,
                    ),
                BINARY_ID to
                    Pair(
                        listOf(
                            Binary(byteArrayOf(1)),
                            Binary(byteArrayOf(2)),
                            Binary(byteArrayOf(3)),
                        ),
                        MongoDbIdType.BINARY,
                    ),
                UUID_ID to
                    Pair(
                        (1..3).map { Binary(BsonBinarySubType.UUID_STANDARD, uuidBytes(it)) },
                        MongoDbIdType.BINARY,
                    ),
                LEGACY_UUID_ID to
                    Pair(
                        (1..3).map { Binary(BsonBinarySubType.UUID_LEGACY, uuidBytes(it)) },
                        MongoDbIdType.BINARY,
                    ),
                DOUBLE_ID to Pair(listOf(1.5, 2.5, 3.5), MongoDbIdType.DOUBLE),
                DECIMAL_ID to
                    Pair(
                        listOf("1.10", "2.20", "3.30").map(Decimal128::parse),
                        MongoDbIdType.DECIMAL,
                    ),
                DATE_ID to
                    Pair(
                        listOf(1_700_000_000_000L, 1_700_000_001_000L, 1_700_000_002_000L)
                            .map(::Date),
                        MongoDbIdType.DATE,
                    ),
                TIMESTAMP_ID to
                    Pair(
                        listOf(
                            BsonTimestamp(1_700_000_000, 1),
                            BsonTimestamp(1_700_000_000, 2),
                            BsonTimestamp(1_700_000_001, 1),
                        ),
                        MongoDbIdType.TIMESTAMP,
                    ),
                // Document `_id`s resume as `BsonDocument` (extended JSON round trip).
                OBJECT_MATRIX_ID to
                    Pair(
                        listOf(1, 2, 3).map {
                            BsonDocument("tenant", BsonString("t1")).append("seq", BsonInt32(it))
                        },
                        MongoDbIdType.OBJECT,
                    ),
            )
        MongoClients.create(replicaSet.connectionString).use { client ->
            collections.forEach { (name, idsAndType) ->
                val coll = client.getDatabase(TEST_DB).getCollection(name)
                coll.drop()
                coll.insertMany(
                    idsAndType.first.mapIndexed { i, id -> Document("_id", id).append("v", i + 1) },
                )
            }
        }
        val result: BufferingOutputConsumer =
            readCutAfter(
                2,
                configuredCatalog(
                    SyncMode.FULL_REFRESH,
                    DestinationSyncMode.OVERWRITE,
                    collections.keys,
                    includeEmpty = false,
                ),
                cursors = collections.size,
            )
        collections.forEach { (name, idsAndType) ->
            val (ids, idType) = idsAndType
            val records = result.records().filter { it.stream == name }
            Assertions.assertEquals(listOf(1, 2, 3), records.map { it.data["v"].asInt() }, name)
            // The first checkpoint is the second `_id`: the third record came from the resumed
            // query.
            val checkpoints: List<MongoDbStreamStateValue> = allStreamStatesFor(result, name)
            Assertions.assertEquals(idType, checkpoints.first().idType, name)
            Assertions.assertEquals(ids[1], checkpoints.first().resumeIdValue(), name)
            Assertions.assertNull(checkpoints.last().id, "$name finished: no _id")
        }
    }

    /** Several configured databases are read through one cluster-wide change stream. */
    @Test
    fun testCdcAcrossMultipleDatabases() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            for (db in listOf(TEST_DB, OTHER_DB)) {
                val coll = client.getDatabase(db).getCollection(MULTI_DB_CDC)
                coll.drop()
                coll.insertOne(Document("_id", 1).append("db", db))
            }
        }
        val config: MongoDbSourceConfigurationSpecification =
            MongoDbTestConfigs.config(replicaSet.connectionString, listOf(TEST_DB, OTHER_DB))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(
                SyncMode.INCREMENTAL,
                DestinationSyncMode.APPEND,
                setOf(MULTI_DB_CDC),
                includeEmpty = false,
                config = config,
            )
        Assertions.assertEquals(
            setOf(TEST_DB, OTHER_DB),
            catalog.streams.map { it.stream.namespace }.toSet(),
        )
        val sync1: BufferingOutputConsumer = read(catalog, config = config)
        Assertions.assertEquals(2, sync1.records().count { it.stream == MULTI_DB_CDC })

        MongoClients.create(replicaSet.connectionString).use { client ->
            for (db in listOf(TEST_DB, OTHER_DB)) {
                client
                    .getDatabase(db)
                    .getCollection(MULTI_DB_CDC)
                    .insertOne(Document("_id", 2).append("db", db))
            }
        }
        val sync2: BufferingOutputConsumer = read(catalog, sync1.states(), config = config)
        val changes = sync2.records().filter { it.stream == MULTI_DB_CDC }
        Assertions.assertEquals(
            setOf(TEST_DB, OTHER_DB),
            changes.map { it.namespace }.toSet(),
            "one change per database",
        )
        Assertions.assertEquals(listOf(2, 2), changes.map { it.data["_id"].asInt() })
    }

    /** Numbers of any width are one `_id` type: the comparison and the resume treat them alike. */
    @Test
    fun testNumericIdWidthsAreOneType() {
        val ids: List<Any> = listOf(1, 2.5, 5_000_000_000L, Decimal128.parse("7000000000.5"))
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(NUMERIC_ID)
            coll.drop()
            coll.insertMany(ids.mapIndexed { i, id -> Document("_id", id).append("v", i + 1) })
        }
        val result: BufferingOutputConsumer =
            readCutAfter(
                2,
                configuredCatalog(
                    SyncMode.FULL_REFRESH,
                    DestinationSyncMode.OVERWRITE,
                    setOf(NUMERIC_ID),
                    includeEmpty = false,
                ),
            )
        val records = result.records().filter { it.stream == NUMERIC_ID }
        Assertions.assertEquals((1..4).toList(), records.map { it.data["v"].asInt() })
        Assertions.assertEquals(emptyList<String>(), mixedIdTypeAnalytics(result), "one type")
        // Resumed after the double 2.5, the round read the long and the decimal.
        val checkpoints: List<MongoDbStreamStateValue> = allStreamStatesFor(result, NUMERIC_ID)
        Assertions.assertEquals(MongoDbIdType.DOUBLE, checkpoints.first().idType)
        Assertions.assertEquals(2.5, checkpoints.first().resumeIdValue())
    }

    /**
     * A collection mixing `_id` kinds is read whole by an uncut round (the scan has no filter), but
     * a resume filter `_id > x` only matches x's kind, so a round resumed after a checkpoint reads
     * the checkpointed kind only — the documented limit of such collections.
     */
    @Test
    fun testMixedIdKindsReadWholeUncutAndOneKindAfterACheckpoint() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(MIXED_ID)
            coll.drop()
            coll.insertMany(
                listOf(1, 2, "a", "b", Date(1_700_000_000_000L)).mapIndexed { i, id ->
                    Document("_id", id).append("v", i + 1)
                },
            )
        }
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(
                SyncMode.FULL_REFRESH,
                DestinationSyncMode.OVERWRITE,
                setOf(MIXED_ID),
                includeEmpty = false,
            )
        val whole: BufferingOutputConsumer = read(catalog)
        Assertions.assertEquals(
            (1..5).toList(),
            recordDataFor(whole, MIXED_ID).map { it["v"] as Int },
        )
        // As the legacy connector did: the mix is warned about and reported once, not refused.
        Assertions.assertEquals(listOf("1"), mixedIdTypeAnalytics(whole))
        val cut: BufferingOutputConsumer = readCutAfter(2, catalog)
        Assertions.assertEquals(listOf(1, 2), recordDataFor(cut, MIXED_ID).map { it["v"] as Int })
        Assertions.assertEquals(2, allStreamStatesFor(cut, MIXED_ID).first().resumeIdValue())
    }

    /** The values of the legacy `db-sources-mongo-multiple-id-types` analytics traces emitted. */
    private fun mixedIdTypeAnalytics(result: BufferingOutputConsumer): List<String> =
        result
            .traces()
            .filter { it.type == AirbyteTraceMessage.Type.ANALYTICS }
            .map { it.analytics }
            .filter { it.type == MongoDbIdTypes.ANALYTICS_KEY }
            .map { it.value }

    /**
     * One document holding every BSON type, read through the connector in both schema modes: each
     * field's emitted value is what the documentation promises (and what the legacy Debezium
     * connector emitted, except the two intentional differences: exact decimals and UTC dates).
     */
    @Test
    fun testEveryBsonTypeIsEmittedAsDocumented() {
        val uuid: UUID = UUID.fromString("123e4567-e89b-12d3-a456-426614174000")
        val uuidBytes: ByteArray = BsonBinary(uuid).data
        val uuidBase64: String = Base64.getEncoder().encodeToString(uuidBytes)
        val document: BsonDocument =
            BsonDocument("_id", BsonObjectId(ObjectId("650000000000000000000099")))
                .append("double", BsonDouble(1.5))
                .append("string", BsonString("text"))
                .append("object", BsonDocument("a", BsonInt32(1)).append("b", BsonString("x")))
                .append(
                    "array",
                    BsonArray(
                        listOf(
                            BsonInt32(1),
                            BsonString("two"),
                            BsonDocument("three", BsonInt32(3)),
                            BsonArray(listOf(BsonInt32(4))),
                        ),
                    ),
                )
                .append("binData", BsonBinary(byteArrayOf(1, 2, 3)))
                .append("uuid", BsonBinary(uuid))
                .append("legacyUuid", BsonBinary(BsonBinarySubType.UUID_LEGACY, uuidBytes))
                .append("vector", BsonBinary(BinaryVector.floatVector(floatArrayOf(1.5f, -2f))))
                .append("undefined", BsonUndefined())
                .append("objectId", BsonObjectId(ObjectId("650000000000000000000001")))
                .append("bool", BsonBoolean(true))
                .append("date", BsonDateTime(1_704_067_200_000L))
                .append("null", BsonNull())
                .append("regex", BsonRegularExpression("^a.c$", "i"))
                .append("regexNoOptions", BsonRegularExpression("abc"))
                .append("dbPointer", BsonDbPointer("db.coll", ObjectId("650000000000000000000002")))
                .append("javascript", BsonJavaScript("function() { return 1; }"))
                .append("symbol", BsonSymbol("sym"))
                .append(
                    "javascriptWithScope",
                    BsonJavaScriptWithScope(
                        "function() { return x; }",
                        BsonDocument("x", BsonInt32(1)),
                    ),
                )
                .append("int", BsonInt32(7))
                .append("timestamp", BsonTimestamp(1_700_000_000, 1))
                .append("long", BsonInt64(9_007_199_254_740_993L))
                .append("decimal", BsonDecimal128(Decimal128.parse("12.34")))
                .append("minKey", BsonMinKey())
                .append("maxKey", BsonMaxKey())
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll =
                client.getDatabase(TEST_DB).getCollection(ALL_TYPES, BsonDocument::class.java)
            coll.drop()
            coll.insertOne(document)
        }
        /** Values that are dropped: absent from the schemaless `data`, `null` as a schema field. */
        val dropped: Set<String> = setOf("undefined", "dbPointer", "minKey", "maxKey")

        fun assertEmitted(data: JsonNode) {
            Assertions.assertEquals(1.5, data["double"].asDouble())
            Assertions.assertEquals("text", data["string"].asText())
            Assertions.assertEquals("""{"a":1,"b":"x"}""", data["object"].toString())
            Assertions.assertEquals("""[1,"two",{"three":3},[4]]""", data["array"].toString())
            Assertions.assertEquals("AQID", data["binData"].asText())
            Assertions.assertEquals(uuidBase64, data["uuid"].asText())
            Assertions.assertEquals(uuidBase64, data["legacyUuid"].asText())
            Assertions.assertEquals(
                Base64.getEncoder().encodeToString(document.getBinary("vector").data),
                data["vector"].asText(),
            )
            Assertions.assertEquals("650000000000000000000001", data["objectId"].asText())
            Assertions.assertTrue(data["bool"].asBoolean())
            Assertions.assertEquals("2024-01-01T00:00:00.000Z", data["date"].asText())
            Assertions.assertTrue(data["null"].isNull)
            Assertions.assertEquals("(i)^a.c$", data["regex"].asText())
            Assertions.assertEquals("abc", data["regexNoOptions"].asText())
            Assertions.assertEquals("function() { return 1; }", data["javascript"].asText())
            Assertions.assertEquals("sym", data["symbol"].asText())
            Assertions.assertEquals(
                """{"code":"function() { return x; }","scope":{"x":1}}""",
                data["javascriptWithScope"].toString(),
            )
            Assertions.assertEquals(7, data["int"].asInt())
            // The raw 64-bit timestamp formatted as epoch milliseconds, no sign on the big year.
            Assertions.assertEquals("231375532-06-01T08:53:20.001Z", data["timestamp"].asText())
            Assertions.assertEquals(9_007_199_254_740_993L, data["long"].asLong())
            Assertions.assertEquals(BigDecimal("12.34"), data["decimal"].decimalValue())
        }

        val enforced: JsonNode =
            read(
                    configuredCatalog(
                        SyncMode.FULL_REFRESH,
                        DestinationSyncMode.OVERWRITE,
                        setOf(ALL_TYPES),
                        includeEmpty = false,
                    ),
                )
                .records()
                .single { it.stream == ALL_TYPES }
                .data
        Assertions.assertEquals("650000000000000000000099", enforced["_id"].asText())
        assertEmitted(enforced)
        dropped.forEach { Assertions.assertTrue(enforced[it].isNull, it) }

        val schemaless: JsonNode =
            read(
                    configuredCatalog(
                        SyncMode.FULL_REFRESH,
                        DestinationSyncMode.OVERWRITE,
                        setOf(ALL_TYPES),
                        includeEmpty = false,
                        config = config(schemaEnforced = false),
                    ),
                    config = config(schemaEnforced = false),
                )
                .records()
                .single { it.stream == ALL_TYPES }
                .data
        Assertions.assertEquals("650000000000000000000099", schemaless["_id"].asText())
        // `data` is the whole document, `_id` included, minus the dropped values.
        Assertions.assertEquals(
            document.keys - dropped,
            schemaless["data"].fieldNames().asSequence().toSet(),
        )
        Assertions.assertEquals("650000000000000000000099", schemaless["data"]["_id"].asText())
        assertEmitted(schemaless["data"])

        // A UUID representation in the connection string must not change how binaries are emitted.
        val standardUuidConfig: MongoDbSourceConfigurationSpecification =
            MongoDbTestConfigs.config(
                "$connectionString&uuidRepresentation=standard",
                listOf(TEST_DB),
            )
        val withUuidRepresentation: JsonNode =
            read(
                    configuredCatalog(
                        SyncMode.FULL_REFRESH,
                        DestinationSyncMode.OVERWRITE,
                        setOf(ALL_TYPES),
                        includeEmpty = false,
                        config = standardUuidConfig,
                    ),
                    config = standardUuidConfig,
                )
                .records()
                .single { it.stream == ALL_TYPES }
                .data
        assertEmitted(withUuidRepresentation)
    }

    @Test
    fun testResumesFromLegacyV2DebeziumStateWithoutReset() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(LEGACY_CDC)
            coll.drop()
            coll.insertOne(Document("_id", ObjectId("670000000000000000000001")).append("v", 1))
        }
        // Sync 1 (cold start) captures a resume token in v3's native state shape.
        val sync1: BufferingOutputConsumer = read(incrementalCatalog(setOf(LEGACY_CDC)))
        Assertions.assertEquals(1, recordCountFor(sync1, LEGACY_CDC))
        val nativeShared = sync1.states().mapNotNull { it.global?.sharedState }.last()
        val tokenData: String = nativeShared["resumeToken"]["_data"].asText()

        // Re-wrap that token exactly as source-mongodb-v2 persisted it (Debezium offset map), with
        // v2's per-stream snapshot state, i.e. the state an upgraded connection would arrive with.
        val legacyState: List<AirbyteStateMessage> =
            listOf(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(
                        AirbyteGlobalState()
                            .withSharedState(legacyV2SharedState(tokenData))
                            .withStreamStates(
                                listOf(
                                    AirbyteStreamState()
                                        .withStreamDescriptor(
                                            StreamDescriptor()
                                                .withName(LEGACY_CDC)
                                                .withNamespace(TEST_DB),
                                        )
                                        .withStreamState(
                                            MongoDbStreamStateValue.fromLastId(
                                                    ObjectId("670000000000000000000001"),
                                                    MongoDbSnapshotStatus.COMPLETE,
                                                )
                                                .toOpaqueStateValue(),
                                        ),
                                ),
                            ),
                    ),
            )

        MongoClients.create(replicaSet.connectionString).use { client ->
            client
                .getDatabase(TEST_DB)
                .getCollection(LEGACY_CDC)
                .insertOne(Document("_id", ObjectId("670000000000000000000002")).append("v", 2))
        }

        // Sync 2 reads the legacy state: no re-snapshot, just the one change since the token.
        val sync2: BufferingOutputConsumer =
            read(incrementalCatalog(setOf(LEGACY_CDC)), legacyState)
        val changes = recordDataFor(sync2, LEGACY_CDC)
        Assertions.assertEquals(
            1,
            changes.size,
            "expected only the post-token insert, got $changes",
        )
        Assertions.assertEquals("670000000000000000000002", changes.single()["_id"])
        // ...and v3 writes its own position going forward while the legacy variables stay as they
        // were, so a downgrade to 2.x resumes from the pre-upgrade position.
        val shared2 = sync2.states().mapNotNull { it.global?.sharedState }.last()
        Assertions.assertTrue(shared2.has("resumeToken"), "expected native state, got $shared2")
        Assertions.assertNotEquals(tokenData, shared2["resumeToken"]["_data"].asText())
        val legacyShared = legacyState.single().global.sharedState
        Assertions.assertEquals(legacyShared["state"], shared2["state"])
        Assertions.assertEquals(legacyShared["schema_enforced"], shared2["schema_enforced"])
    }

    /** v2's `shared_state`: `MongoDbDebeziumStateUtil.formatState` wrapped in `MongoDbCdcState`. */
    private fun legacyV2SharedState(tokenData: String): JsonNode {
        val key = """["source-mongodb-v2",{"server_id":"localhost"}]"""
        val value = """{"sec":1727740800,"ord":1,"resume_token":"$tokenData"}"""
        return Jsons.objectNode().apply {
            set<JsonNode>(
                "state",
                Jsons.objectNode().put(key, value),
            )
            put("schema_enforced", true)
        }
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
                "and saved state (false). Please refresh or clear your data.",
        )
    }

    @Test
    fun testInvalidResumeTokenFailsSyncByDefault() {
        val state = globalState(MongoDbSnapshotStatus.COMPLETE, resumeToken = BOGUS_RESUME_TOKEN)
        // A token the server cannot parse is a corrupt state, not an oplog-retention problem.
        assertReadFails(incrementalCatalog(), state, "please refresh or clear the connection")
    }

    @Test
    fun testInvalidResumeTokenResyncsWhenConfigured() {
        val resync =
            MongoDbTestConfigs.config(
                connectionString,
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

    /** [MongoDbReadTestSupport.readCutAfter] on this class's replica set and config. */
    private fun readCutAfter(
        after: Int,
        catalog: ConfiguredAirbyteCatalog,
        cursors: Int = 1,
    ): BufferingOutputConsumer =
        MongoDbReadTestSupport.readCutAfter(replicaSet, after, config(), catalog, cursors = cursors)

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
            includeEmpty = false,
        )

    /** Builds a configured catalog from the connector's own discover output. */
    private fun configuredCatalog(
        syncMode: SyncMode,
        destinationSyncMode: DestinationSyncMode,
        names: Set<String>,
        includeEmpty: Boolean,
        config: MongoDbSourceConfigurationSpecification = config(),
    ): ConfiguredAirbyteCatalog {
        val discovered = CliRunner.source("discover", config).run().catalogs().first()
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
        stream: String,
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
                record.data.properties().asSequence().associate { (k, v) ->
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

    /** All snapshot checkpoints emitted for a stream, in order, to observe resume progress. */
    private fun allStreamStatesFor(
        result: BufferingOutputConsumer,
        stream: String,
    ): List<MongoDbStreamStateValue> =
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
                runCatching { MongoDbStreamStateValue.fromOpaqueStateValue(it.streamState) }
                    .getOrNull()
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
        const val OTHER_DB = "other_db"
        const val MULTI_DB_CDC = "multi_db_cdc_coll"
        const val PEOPLE = "people"
        const val EMPTY = "empty_coll"
        const val CDC = "cdc_coll"
        const val BUSY_CDC = "busy_cdc_coll"
        const val PRE_IMAGE_CDC = "pre_image_cdc_coll"
        const val CODE_ID = "code_id_coll"
        const val LEGACY_CDC = "legacy_cdc_coll"
        const val DOC_ID = "doc_id_coll"
        const val NOTHING_LEFT = "nothing_left_coll"
        const val OBJECT_MATRIX_ID = "object_matrix_id_coll"
        const val ALL_TYPES = "all_types_coll"
        const val STRING_ID = "string_id_coll"
        const val INT_ID = "int_id_coll"
        const val LONG_ID = "long_id_coll"
        const val BINARY_ID = "binary_id_coll"
        const val UUID_ID = "uuid_id_coll"
        const val LEGACY_UUID_ID = "legacy_uuid_id_coll"
        const val DOUBLE_ID = "double_id_coll"
        const val DECIMAL_ID = "decimal_id_coll"
        const val DATE_ID = "date_id_coll"
        const val TIMESTAMP_ID = "timestamp_id_coll"
        const val NUMERIC_ID = "numeric_id_coll"
        const val MIXED_ID = "mixed_id_coll"
        /**
         * A `_data` the server rejects (`FailedToParse`, not a hex string). Note that any
         * *well-formed* token is accepted and resumed from the oplog start, so a rejected token is
         * the only way to exercise the invalid-token path against a live replica set.
         */
        const val BOGUS_RESUME_TOKEN = "garbage"

        lateinit var replicaSet: MongoDBContainer

        /** The connection string the connector is given (failpoints target its `appName`). */
        val connectionString: String
            get() = MongoDbReadTestSupport.connectorConnectionString(replicaSet)

        fun config(schemaEnforced: Boolean = true): MongoDbSourceConfigurationSpecification =
            MongoDbTestConfigs.config(
                connectionString,
                listOf(TEST_DB),
                schemaEnforced = schemaEnforced,
            )

        /** The 16 bytes of a UUID whose last byte is [n]. */
        fun uuidBytes(n: Int): ByteArray = BsonBinary(UUID(0L, n.toLong())).data

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
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
