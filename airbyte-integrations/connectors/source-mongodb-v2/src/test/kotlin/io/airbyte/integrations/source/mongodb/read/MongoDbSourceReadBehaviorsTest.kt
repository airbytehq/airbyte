/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.mongodb.client.MongoClients
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.alwaysOn
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.assertFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.configuredCatalog
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.discover
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.failing
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.read
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.readExpectingFailure
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.records
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.statuses
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.withFailPoint
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import java.util.Date
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer

/**
 * Read behaviours that follow from the configured catalog and the catalog's life cycle rather than
 * from the data: deselected, absent and extra fields, the array and `_aibyte_transform` catalog
 * rules end to end, schemaless incremental syncs, replace and repeated updates, states and
 * collections the catalog no longer matches, and a catalog of many collections.
 */
class MongoDbSourceReadBehaviorsTest {

    /**
     * The catalog decides what a record holds: a deselected field is not emitted, a field absent
     * from the document is `null`, a scalar in a field the catalog declares `array` is wrapped, and
     * a `<field>_aibyte_transform` property receives the field JSON-stringified while the field
     * itself is nulled. A document's fields outside the catalog never leave the server.
     */
    @Test
    fun testDeselectedAbsentWrappedAndTransformedFieldsFollowTheCatalog() {
        seed(
            SHAPED,
            Document("_id", 1)
                .append("name", "alice")
                .append("dropped", "never emitted")
                .append("tags", "single")
                .append("addr", Document("city", "Paris")),
        )
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(SHAPED))
        val properties: ObjectNode =
            catalog.streams.single().stream.jsonSchema["properties"] as ObjectNode
        properties.remove("dropped")
        properties.set<JsonNode>("missing", Jsons.readTree("""{"type":"string"}"""))
        properties.set<JsonNode>("tags", Jsons.readTree("""{"type":"array"}"""))
        properties.set<JsonNode>("addr_aibyte_transform", Jsons.readTree("""{"type":"string"}"""))

        val record: JsonNode = records(read(config(), catalog), SHAPED).single()
        Assertions.assertEquals("alice", record["name"].asText())
        Assertions.assertFalse(record.has("dropped"), "deselected: $record")
        Assertions.assertTrue(record["missing"].isNull, "absent from the document: $record")
        Assertions.assertEquals("""["single"]""", record["tags"].toString(), "wrapped: $record")
        Assertions.assertEquals("""{"city":"Paris"}""", record["addr_aibyte_transform"].asText())
        Assertions.assertTrue(record["addr"].isNull, "the transformed field is nulled: $record")
    }

    /** Schemaless mode through the change stream: `{_id, data}` for changes and deletes alike. */
    @Test
    fun testSchemalessIncrementalSyncEmitsIdAndData() {
        seed(
            SCHEMALESS,
            Document("_id", 1).append("v", "one"),
            Document("_id", 2).append("v", "two")
        )
        val config: MongoDbSourceConfigurationSpecification = config(schemaEnforced = false)
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config, SyncMode.INCREMENTAL, setOf(SCHEMALESS))
        Assertions.assertEquals(
            setOf("_id", "data", "_ab_cdc_updated_at", "_ab_cdc_deleted_at", "_ab_cdc_cursor"),
            catalog.streams
                .single()
                .stream
                .jsonSchema["properties"]
                .fieldNames()
                .asSequence()
                .toSet(),
        )
        val sync1: BufferingOutputConsumer = read(config, catalog)
        Assertions.assertEquals(
            listOf("one", "two"),
            records(sync1, SCHEMALESS).map { it["data"]["v"].asText() },
        )

        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(SCHEMALESS)
            coll.insertOne(
                Document("_id", 3).append("v", "three").append("nested", Document("k", 1))
            )
            coll.updateOne(Filters.eq("_id", 1), Updates.set("v", "uno"))
            coll.deleteOne(Filters.eq("_id", 2))
        }
        val sync2: BufferingOutputConsumer = read(config, catalog, sync1.states())
        val changes: Map<Int, JsonNode> =
            records(sync2, SCHEMALESS).associateBy { it["_id"].asInt() }
        Assertions.assertEquals(setOf(1, 2, 3), changes.keys)
        Assertions.assertEquals("uno", changes.getValue(1)["data"]["v"].asText())
        Assertions.assertEquals(1, changes.getValue(3)["data"]["nested"]["k"].asInt())
        val deleted: JsonNode = changes.getValue(2)
        Assertions.assertFalse(deleted["_ab_cdc_deleted_at"].isNull)
        Assertions.assertEquals(
            2,
            deleted["data"]["_id"].asInt(),
            "a delete carries the key: $deleted"
        )
    }

    /**
     * A replace drops the fields it does not carry; every update of a document updated many times
     * between syncs is an event, each looked up as the document's state at read time (so all show
     * the final state), with strictly increasing cursors.
     */
    @Test
    fun testReplaceAndRepeatedUpdatesOfOneDocument() {
        seed(
            STORM,
            Document("_id", 1).append("v", "one").append("old", true),
            Document("_id", 2).append("n", 0),
        )
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(STORM))
        val sync1: BufferingOutputConsumer = read(config(), catalog)
        Assertions.assertEquals(2, records(sync1, STORM).size)

        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(STORM)
            coll.replaceOne(Filters.eq("_id", 1), Document("v", "replaced"))
            repeat(UPDATES) { coll.updateOne(Filters.eq("_id", 2), Updates.inc("n", 1)) }
        }
        val sync2: BufferingOutputConsumer = read(config(), catalog, sync1.states())
        val changes: List<JsonNode> = records(sync2, STORM)
        val replaced: JsonNode = changes.single { it["_id"].asInt() == 1 }
        Assertions.assertEquals("replaced", replaced["v"].asText())
        Assertions.assertTrue(
            replaced["old"].isNull,
            "a replace drops the fields it lacks: $replaced"
        )
        val storm: List<JsonNode> = changes.filter { it["_id"].asInt() == 2 }
        Assertions.assertEquals(UPDATES, storm.size, "one event per update")
        Assertions.assertTrue(
            storm.all { it["n"].asInt() == UPDATES },
            "each looked up at read time"
        )
        val cursors: List<Long> = storm.map { it["_ab_cdc_cursor"].asLong() }
        Assertions.assertEquals(cursors.sorted().distinct(), cursors, "strictly increasing cursors")
    }

    /**
     * A full-refresh-only sync writes a shared state with no position (the schema mode only). The
     * platform hands that state back as-is; it must start a later sync — here one that adds an
     * incremental stream, whose cold start captures a position.
     */
    @Test
    fun testFullRefreshOnlySyncStateCanStartAnIncrementalSync() {
        seed(PLAIN, Document("_id", 1).append("v", "one"))
        seed(ADDED, Document("_id", 1).append("v", "first"))
        val fullRefresh: BufferingOutputConsumer =
            read(config(), configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(PLAIN)))
        val shared: JsonNode = fullRefresh.states().mapNotNull { it.global?.sharedState }.last()
        Assertions.assertFalse(shared.hasNonNull("resumeToken"), "no position: $shared")
        Assertions.assertTrue(shared["schemaEnforced"].asBoolean())

        val withIncremental: ConfiguredAirbyteCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(PLAIN)).streams +
                        configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(ADDED)).streams
                )
        val sync2: BufferingOutputConsumer = read(config(), withIncremental, fullRefresh.states())
        Assertions.assertEquals(listOf("one"), records(sync2, PLAIN).map { it["v"].asText() })
        Assertions.assertEquals(listOf("first"), records(sync2, ADDED).map { it["v"].asText() })
        Assertions.assertTrue(
            sync2.states().mapNotNull { it.global?.sharedState }.last().hasNonNull("resumeToken"),
            "the cold start captured a position",
        )
        MongoClients.create(replicaSet.connectionString).use {
            it.getDatabase(TEST_DB)
                .getCollection(ADDED)
                .insertOne(Document("_id", 2).append("v", "second"))
        }
        val sync3: BufferingOutputConsumer = read(config(), withIncremental, sync2.states())
        Assertions.assertEquals(listOf("second"), records(sync3, ADDED).map { it["v"].asText() })
    }

    /**
     * The full-refresh state contract: the checkpoint of an interrupted full refresh carries the
     * last `_id` and a sync given it resumes after that `_id`; the checkpoint of a finished one
     * carries no `_id` and a sync given it reads the collection again from the start.
     */
    @Test
    fun testFullRefreshResumesWhenInterruptedAndStartsOverWhenFinished() {
        seed(RESTART, *(1..5).map { Document("_id", it) }.toTypedArray())
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(RESTART))
        val interrupted: List<AirbyteStateMessage> =
            listOf(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(
                        AirbyteGlobalState()
                            .withSharedState(Jsons.readTree("""{"schemaEnforced": true}"""))
                            .withStreamStates(
                                listOf(
                                    AirbyteStreamState()
                                        .withStreamDescriptor(
                                            StreamDescriptor()
                                                .withName(RESTART)
                                                .withNamespace(TEST_DB)
                                        )
                                        .withStreamState(
                                            Jsons.readTree(
                                                """{"id":"3","status":"FULL_REFRESH","idType":"INT","binarySubType":0}"""
                                            )
                                        ),
                                )
                            ),
                    ),
            )
        val resumed: BufferingOutputConsumer = read(config(), catalog, interrupted)
        Assertions.assertEquals(listOf(4, 5), records(resumed, RESTART).map { it["_id"].asInt() })
        val finished = MongoDbReadTestSupport.lastStreamState(resumed, RESTART)
        Assertions.assertNull(finished?.id, "finished: no _id")

        val startedOver: BufferingOutputConsumer = read(config(), catalog, resumed.states())
        Assertions.assertEquals(
            (1..5).toList(),
            records(startedOver, RESTART).map { it["_id"].asInt() },
        )
    }

    /** A stream state the connector cannot read fails the sync instead of restarting silently. */
    @Test
    fun testUnreadableStreamStateFailsTheSync() {
        seed(PLAIN, Document("_id", 1))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(PLAIN))
        val state: List<AirbyteStateMessage> =
            listOf(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(
                        AirbyteGlobalState()
                            .withSharedState(
                                Jsons.readTree("""{"resumeToken": null, "schemaEnforced": true}""")
                            )
                            .withStreamStates(
                                listOf(
                                    AirbyteStreamState()
                                        .withStreamDescriptor(
                                            StreamDescriptor()
                                                .withName(PLAIN)
                                                .withNamespace(TEST_DB)
                                        )
                                        .withStreamState(Jsons.readTree("""{"foo": 1}""")),
                                )
                            ),
                    ),
            )
        val failed: BufferingOutputConsumer = readExpectingFailure(config(), catalog, state)
        assertFailure(
            failed,
            FailureType.CONFIG_ERROR,
            "Failed to migrate to the new connector version state protocol",
        )
    }

    /**
     * A collection dropped after the schema was discovered: the CDK's catalog validation marks the
     * stream `INCOMPLETE` and aborts the sync rather than advance the CDC position past data it
     * could not read.
     */
    @Test
    fun testDroppedCollectionInTheCatalogAbortsTheSync() {
        seed(PLAIN, Document("_id", 1))
        seed(DROPPED, Document("_id", 1).append("v", "gone"))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(PLAIN, DROPPED))
        MongoClients.create(replicaSet.connectionString).use {
            it.getDatabase(TEST_DB).getCollection(DROPPED).drop()
        }
        val failed: BufferingOutputConsumer = readExpectingFailure(config(), catalog)
        assertFailure(
            failed,
            FailureType.CONFIG_ERROR,
            "could not be read due to catalog validation errors"
        )
        Assertions.assertEquals(
            listOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.INCOMPLETE),
            statuses(failed, DROPPED),
        )
    }

    /** A failing stream is reported `INCOMPLETE`; the others in the sync still finish. */
    @Test
    fun testFailingStreamIsIncompleteWhileOthersComplete() {
        seed(PLAIN, Document("_id", 1))
        seed(MIXED, Document("_id", 1), Document("_id", "two"))
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(PLAIN, MIXED))
        // Every `find` on one collection is refused as unauthorized: a configuration error.
        val failed: BufferingOutputConsumer =
            withFailPoint(
                replicaSet,
                alwaysOn(),
                failing("find", errorCode = 13).append("namespace", "$TEST_DB.$MIXED"),
            ) {
                readExpectingFailure(config(), catalog)
            }
        assertFailure(failed, FailureType.CONFIG_ERROR, "Unauthorized")
        Assertions.assertEquals(
            listOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.INCOMPLETE),
            statuses(failed, MIXED),
        )
        Assertions.assertEquals(
            listOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE),
            statuses(failed, PLAIN),
        )
    }

    /** Discovery and a full read of a database with many collections. */
    @Test
    fun testManyCollectionsAreDiscoveredAndReadInFull() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val db = client.getDatabase(MANY_DB)
            (1..MANY).forEach { n ->
                db.getCollection("c$n")
                    .insertMany((1..3).map { Document("_id", it).append("c", n) })
            }
        }
        val config: MongoDbSourceConfigurationSpecification =
            MongoDbReadTestSupport.config(replicaSet, listOf(MANY_DB))
        val names: Set<String> = (1..MANY).map { "c$it" }.toSet()
        Assertions.assertEquals(names, discover(config).streams.map { it.name }.toSet())
        val result: BufferingOutputConsumer =
            read(config, configuredCatalog(config, SyncMode.FULL_REFRESH, names))
        Assertions.assertEquals(MANY * 3, result.records().size)
        names.forEach { name ->
            Assertions.assertEquals(
                listOf(AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE),
                statuses(result, name),
                name,
            )
        }
    }

    /** A field holding different types across documents gets one of them, never fails. */
    @Test
    fun testDiscoverTypesAMixedFieldAsOneOfItsTypes() {
        seed(
            MIXED_FIELD,
            Document("_id", 1).append("flex", "text"),
            Document("_id", 2).append("flex", 42),
            Document("_id", 3).append("flex", Date(0)),
        )
        val stream = discover(config()).streams.single { it.name == MIXED_FIELD }
        val type: String = stream.jsonSchema["properties"]["flex"]["type"].asText()
        Assertions.assertTrue(type in setOf("string", "number"), type)
    }

    /** A sample of at least the collection's size sees every field, rare ones included. */
    @Test
    fun testDiscoverSampleCoveringTheCollectionFindsRareFields() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(RARE)
            coll.drop()
            coll.insertMany((1..999).map { Document("_id", it).append("common", it) })
            coll.insertOne(Document("_id", 1000).append("common", 1000).append("rare", true))
        }
        val config: MongoDbSourceConfigurationSpecification =
            MongoDbReadTestSupport.config(
                replicaSet,
                listOf(TEST_DB),
                extraRootProperties = mapOf("discover_sample_size" to 1000),
            )
        val stream = discover(config).streams.single { it.name == RARE }
        Assertions.assertEquals(
            setOf(
                "_id",
                "common",
                "rare",
                "_ab_cdc_updated_at",
                "_ab_cdc_deleted_at",
                "_ab_cdc_cursor"
            ),
            stream.jsonSchema["properties"].fieldNames().asSequence().toSet(),
        )
    }

    private fun seed(collection: String, vararg documents: Document) {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(collection)
            coll.drop()
            coll.insertMany(documents.toList())
        }
    }

    private fun config(schemaEnforced: Boolean? = null): MongoDbSourceConfigurationSpecification =
        MongoDbReadTestSupport.config(replicaSet, listOf(TEST_DB), schemaEnforced = schemaEnforced)

    companion object {
        const val TEST_DB = "behaviors_db"
        const val MANY_DB = "many_db"
        const val SHAPED = "shaped"
        const val SCHEMALESS = "schemaless"
        const val STORM = "storm"
        const val PLAIN = "plain"
        const val DROPPED = "dropped"
        const val ADDED = "added"
        const val RESTART = "restart"
        const val MIXED = "mixed"
        const val MIXED_FIELD = "mixed_field"
        const val RARE = "rare"
        const val UPDATES = 20
        const val MANY = 150

        lateinit var replicaSet: MongoDBContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }
    }
}
