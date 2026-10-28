/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.integrations.source.mongodb.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.bson.BsonDocument
import org.bson.BsonString
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.types.ObjectId
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer

/** The diagnostic lines, built against a live replica set. */
class MongoDbDiagnosticsTest {

    @Test
    fun testConnectionLine() {
        val configuration: MongoDbSourceConfiguration =
            MongoDbSourceConfigurationFactory()
                .makeWithoutExceptionHandling(
                    MongoDbTestConfigs.config(replicaSet.connectionString, listOf(TEST_DB)),
                )
        val line: String =
            MongoDbDiagnostics.connectionLine(
                client,
                MongoDbClientFactory.settings(configuration),
            )
        Assertions.assertTrue(line.startsWith("Connected to MongoDB 7.0."), line)
        for (part in
            listOf(
                "replica set \"docker-rs\"",
                "answering member ",
                "(primary)",
                "hosts [",
                "wire version 21",
                "TLS off",
                "read preference secondaryPreferred",
                "compression requested snappy,zlib",
            )) {
            Assertions.assertTrue(part in line, "'$part' in: $line")
        }
    }

    @Test
    fun testOplogLineAndTheSavedPositionInItsWindow() {
        val line: String = MongoDbDiagnostics.oplogLine(client, savedToken = null)
        Assertions.assertTrue(OPLOG_LINE.matches(line), line)

        val newest: BsonTimestamp = checkNotNull(oplogEndpoint(-1))
        val inside: String = MongoDbDiagnostics.oplogLine(client, tokenAt(newest))
        Assertions.assertTrue(" h inside the window." in inside, inside)

        val ancient: String = MongoDbDiagnostics.oplogLine(client, tokenAt(BsonTimestamp(1, 0)))
        Assertions.assertTrue(
            "is OLDER than the oldest entry: the change stream cannot resume from it." in ancient,
            ancient,
        )
    }

    /** A malformed saved token is this line's failure, reported by the guard, not the sync's. */
    @Test
    fun testMalformedSavedTokenFailsOnlyTheLine() {
        val garbage = BsonDocument("_data", BsonString("garbage"))
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            MongoDbDiagnostics.oplogLine(client, garbage)
        }
        Assertions.assertDoesNotThrow {
            MongoDbDiagnostics.logGuarded("the oplog statistics") {
                MongoDbDiagnostics.oplogLine(client, garbage)
            }
        }
    }

    @Test
    fun testCollectionLineCountsSizesIndexesAndTheIdTypes() {
        val line: String = MongoDbDiagnostics.collectionLine(client, stream(PEOPLE))
        Assertions.assertTrue(COLLECTION_LINE.matches(line), line)
        Assertions.assertTrue(
            line.startsWith("Snapshot of $TEST_DB.$PEOPLE: 1,500 documents, "),
            line,
        )
        Assertions.assertTrue(line.endsWith(", 2 indexes; _id types [objectId]."), line)

        val empty: String = MongoDbDiagnostics.collectionLine(client, stream(EMPTY))
        Assertions.assertTrue(
            empty.startsWith("Snapshot of $TEST_DB.$EMPTY: 0 documents, 0 B, "),
            empty,
        )
        Assertions.assertFalse("_id types" in empty, empty)
    }

    /** A diagnostic that cannot be built is a warning, never an exception. */
    @Test
    fun testGuardedLoggingNeverThrows() {
        Assertions.assertDoesNotThrow {
            MongoDbDiagnostics.logGuarded("a failing diagnostic") { error("boom") }
        }
        Assertions.assertDoesNotThrow {
            MongoDbDiagnostics.logGuarded("a missing collection") {
                MongoDbDiagnostics.collectionLine(
                    client,
                    StreamIdentifier.from(
                        StreamDescriptor().withName("missing").withNamespace("no_such_db"),
                    ),
                )
            }
        }
    }

    private fun stream(name: String): StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName(name).withNamespace(TEST_DB))

    /** A resume token whose KeyString starts with [time]: the type byte `0x82` then the 8 bytes. */
    private fun tokenAt(time: BsonTimestamp): BsonDocument =
        BsonDocument("_data", BsonString("82%016X2B0429296E1404".format(time.value)))

    private fun oplogEndpoint(order: Int): BsonTimestamp? =
        client
            .getDatabase("local")
            .getCollection("oplog.rs")
            .find()
            .sort(Document("\$natural", order))
            .limit(1)
            .first()
            ?.get("ts", BsonTimestamp::class.java)

    companion object {
        const val TEST_DB = "diagnostics_db"
        const val PEOPLE = "people"
        const val EMPTY = "empty"

        /** `Oplog: 4.5 KB used of 40.1 GB, 22 entries, <instant> to <instant> (window 0.0 h).` */
        val OPLOG_LINE =
            Regex(
                """Oplog: [\d.]+ (B|KB|MB|GB) used of [\d.]+ (B|KB|MB|GB), [\d,]+ entries, """ +
                    """\S+Z to \S+Z \(window [\d.]+ h\)\.""",
            )
        val COLLECTION_LINE =
            Regex(
                """Snapshot of \S+: [\d,]+ documents, [\d.]+ (B|KB|MB|GB) \(avg [\d.]+ (B|KB|MB|GB)\), """ +
                    """[\d.]+ (B|KB|MB|GB) on disk, \d+ indexes; _id types \[[\w, ]+\]\.""",
            )

        lateinit var replicaSet: MongoDBContainer
        lateinit var client: MongoClient

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
            client = MongoClients.create(replicaSet.connectionString)
            val db = client.getDatabase(TEST_DB)
            db.getCollection(PEOPLE)
                .insertMany(
                    (1..1500).map { Document("_id", ObjectId()).append("name", "person $it") },
                )
            db.getCollection(PEOPLE).createIndex(Document("name", 1))
            db.createCollection(EMPTY)
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            client.close()
            replicaSet.stop()
        }
    }
}
