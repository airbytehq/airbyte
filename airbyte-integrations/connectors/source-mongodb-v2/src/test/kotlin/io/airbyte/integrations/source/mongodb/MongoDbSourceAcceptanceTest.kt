/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.airbyte.protocol.models.v0.AirbyteCatalog
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
 * End-to-end acceptance test for the standard connector flow (spec → check → discover → read)
 * against a real replica set, with a datatype matrix. This is the substantive replacement for the
 * deprecated Python Connector Acceptance Tests (see `acceptance-test-config.yml`).
 */
class MongoDbSourceAcceptanceTest {

    @Test
    fun testCheckSucceeds() {
        SyncsTestFixture.testCheck(config())
    }

    @Test
    fun testDiscoverExposesTheCollection() {
        val catalog: AirbyteCatalog =
            CliRunner.source("discover", config()).run().catalogs().first()
        val stream = catalog.streams.firstOrNull { it.name == COLLECTION }
        Assertions.assertNotNull(stream, "expected the $COLLECTION stream in the catalog")
        Assertions.assertEquals(
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            stream!!.supportedSyncModes,
        )
    }

    @Test
    fun testFullRefreshReadRoundTripsEveryDatatype() {
        val result: BufferingOutputConsumer =
            read(SyncMode.FULL_REFRESH, DestinationSyncMode.OVERWRITE)
        val records = result.records().filter { it.stream == COLLECTION }
        Assertions.assertEquals(1, records.size)
        val data = records.first().data

        Assertions.assertEquals("650000000000000000000001", data["_id"].asText())
        Assertions.assertEquals("hello", data["str"].asText())
        Assertions.assertEquals(42, data["int"].asInt())
        Assertions.assertEquals(9007199254740993L, data["long"].asLong())
        Assertions.assertEquals(1.5, data["dbl"].asDouble())
        Assertions.assertEquals(BigDecimal("12.34"), data["dec"].decimalValue())
        Assertions.assertTrue(data["bool"].asBoolean())
        Assertions.assertEquals(listOf("a", "b"), data["arr"].map { it.asText() })
        Assertions.assertEquals("Paris", data["obj"]["city"].asText())
    }

    @Test
    fun testIncrementalReadEmitsCompleteState() {
        val result: BufferingOutputConsumer = read(SyncMode.INCREMENTAL, DestinationSyncMode.APPEND)
        Assertions.assertEquals(1, result.records().count { it.stream == COLLECTION })
        val state =
            result
                .states()
                .flatMap { it.global?.streamStates ?: emptyList() }
                .last { it.streamDescriptor.name == COLLECTION }
        Assertions.assertEquals(
            MongoDbSnapshotStatus.COMPLETE,
            MongoDbStreamStateValue.fromOpaqueStateValue(state.streamState).status,
        )
    }

    private fun read(
        syncMode: SyncMode,
        destinationSyncMode: DestinationSyncMode,
    ): BufferingOutputConsumer {
        val discovered = CliRunner.source("discover", config()).run().catalogs().first()
        val configured =
            discovered.streams
                .filter { it.name == COLLECTION }
                .map { stream ->
                    ConfiguredAirbyteStream()
                        .withStream(stream)
                        .withSyncMode(syncMode)
                        .withDestinationSyncMode(destinationSyncMode)
                        .withCursorField(stream.defaultCursorField)
                        .withPrimaryKey(stream.sourceDefinedPrimaryKey)
                }
        return CliRunner.source(
                "read",
                config(),
                ConfiguredAirbyteCatalog().withStreams(configured)
            )
            .run()
    }

    companion object {
        const val DATABASE = "acceptance_db"
        const val COLLECTION = "datatypes"

        lateinit var replicaSet: MongoDBContainer

        fun config(): MongoDbSourceConfigurationSpecification =
            MongoDbTestConfigs.config(replicaSet.connectionString, listOf(DATABASE))

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
            client
                .getDatabase(DATABASE)
                .getCollection(COLLECTION)
                .insertOne(
                    Document("_id", ObjectId("650000000000000000000001"))
                        .append("str", "hello")
                        .append("int", 42)
                        .append("long", 9007199254740993L)
                        .append("dbl", 1.5)
                        .append("dec", Decimal128(BigDecimal("12.34")))
                        .append("bool", true)
                        .append("arr", listOf("a", "b"))
                        .append("obj", Document("city", "Paris")),
                )
        }
    }
}
