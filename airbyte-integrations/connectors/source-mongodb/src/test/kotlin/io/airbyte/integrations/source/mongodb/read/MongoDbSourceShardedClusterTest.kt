/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.MongoClients
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.MongoDbDiagnostics
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.configuredCatalog
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.read
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.records
import io.airbyte.integrations.source.mongodb.MongoDbTestConfigs
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * A sharded cluster reached through `mongos` (config server, one shard, the collection sharded on a
 * hashed `_id`): `check` passes the `SHARDED` cluster type, the snapshot reads and resumes through
 * `mongos`, and the change stream delivers changes.
 */
class MongoDbSourceShardedClusterTest {

    @Test
    fun testCheckPassesOnAShardedCluster() {
        SyncsTestFixture.testCheck(config())
    }

    /**
     * The snapshot reads the sharded collection through `mongos`, and resumes after a checkpoint.
     */
    @Test
    fun testSnapshotResumesThroughMongos() {
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.FULL_REFRESH, setOf(PEOPLE))
        Assertions.assertEquals(
            (1..DOCUMENTS).toList(),
            records(read(config(), catalog), PEOPLE).map { it["_id"].asInt() },
        )
        // An interrupted full refresh checkpointed at _id=40: the retry continues after it.
        val checkpoint: List<AirbyteStateMessage> =
            listOf(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(
                        AirbyteGlobalState()
                            .withSharedState(
                                MongoDbCdcState.of(null, true, null).toOpaqueStateValue(),
                            )
                            .withStreamStates(
                                listOf(
                                    AirbyteStreamState()
                                        .withStreamDescriptor(
                                            StreamDescriptor()
                                                .withName(PEOPLE)
                                                .withNamespace(TEST_DB),
                                        )
                                        .withStreamState(
                                            MongoDbStreamStateValue.fromLastId(
                                                    40,
                                                    MongoDbSnapshotStatus.FULL_REFRESH,
                                                )
                                                .toOpaqueStateValue(),
                                        ),
                                ),
                            ),
                    ),
            )
        Assertions.assertEquals(
            (41..DOCUMENTS).toList(),
            records(read(config(), catalog, checkpoint), PEOPLE).map { it["_id"].asInt() },
        )
    }

    /** Through `mongos` the oplog is out of reach, and collection statistics come per shard. */
    @Test
    fun testDiagnosticsThroughMongos() {
        MongoClients.create(mongos.connectionString).use { client ->
            Assertions.assertEquals(
                "Oplog statistics are per shard and not available through mongos.",
                MongoDbDiagnostics.oplogLine(client, savedToken = null),
            )
            val line: String =
                MongoDbDiagnostics.collectionLine(
                    client,
                    StreamIdentifier.from(
                        StreamDescriptor().withName(PEOPLE).withNamespace(TEST_DB),
                    ),
                )
            Assertions.assertTrue(
                line.startsWith("Snapshot of $TEST_DB.$PEOPLE: $DOCUMENTS documents, "),
                line,
            )
            Assertions.assertTrue(line.endsWith("; _id types [number]."), line)
        }
    }

    @Test
    fun testChangeStreamThroughMongos() {
        val catalog: ConfiguredAirbyteCatalog =
            configuredCatalog(config(), SyncMode.INCREMENTAL, setOf(CHANGES))
        val sync1: BufferingOutputConsumer = read(config(), catalog)
        Assertions.assertEquals(2, records(sync1, CHANGES).size)

        MongoClients.create(mongos.connectionString).use { client ->
            val coll = client.getDatabase(TEST_DB).getCollection(CHANGES)
            coll.insertOne(Document("_id", 3).append("v", "new"))
            coll.updateOne(Filters.eq("_id", 1), Updates.set("v", "updated"))
            coll.deleteOne(Filters.eq("_id", 2))
        }
        val sync2: BufferingOutputConsumer = read(config(), catalog, sync1.states())
        val changes: List<JsonNode> = records(sync2, CHANGES)
        Assertions.assertEquals(3, changes.size, "insert + update + delete: $changes")
        Assertions.assertEquals("updated", changes.single { it["_id"].asInt() == 1 }["v"].asText())
        Assertions.assertFalse(
            changes.single { it["_id"].asInt() == 2 }["_ab_cdc_deleted_at"].isNull,
        )
    }

    private fun config(): MongoDbSourceConfigurationSpecification =
        MongoDbTestConfigs.config(mongos.connectionString, listOf(TEST_DB))

    companion object {
        const val TEST_DB = "sharded_db"
        const val PEOPLE = "people"
        const val CHANGES = "changes"
        const val DOCUMENTS = 100

        lateinit var mongos: MongoDBContainer

        @JvmStatic
        @BeforeAll
        fun startCluster() {
            mongos =
                MongoDBContainer(DockerImageName.parse("mongo:7.0")).withSharding().also {
                    it.start()
                }
            val sharding =
                mongos.execInContainer(
                    "mongosh",
                    "--quiet",
                    "--eval",
                    "sh.enableSharding('$TEST_DB'); " +
                        "sh.shardCollection('$TEST_DB.$PEOPLE', {_id: 'hashed'}); " +
                        "sh.shardCollection('$TEST_DB.$CHANGES', {_id: 'hashed'});",
                )
            check(sharding.exitCode == 0) { sharding.stderr + sharding.stdout }
            MongoClients.create(mongos.connectionString).use { client ->
                client
                    .getDatabase(TEST_DB)
                    .getCollection(PEOPLE)
                    .insertMany((1..DOCUMENTS).map { Document("_id", it).append("v", "v$it") })
                client
                    .getDatabase(TEST_DB)
                    .getCollection(CHANGES)
                    .insertMany((1..2).map { Document("_id", it).append("v", "v$it") })
            }
        }

        @JvmStatic
        @AfterAll
        fun stopCluster() {
            mongos.stop()
        }
    }
}
