/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.discover

import com.mongodb.client.MongoClients
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.integrations.source.mongodb.MongoDbTestConfigs
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * A field that is a string in some documents and explicit BSON null in the rest must be discovered
 * as `string` on every run. `$group` does not order document shapes, so the null shape used to win
 * the `putIfAbsent` race and the catalog came back `{"type": "null"}`.
 */
class MongoDbNullFieldDiscoveryTest {

    @Test
    fun testExplicitNullDoesNotHideARealType() {
        val config =
            MongoDbSourceConfigurationFactory()
                .make(
                    MongoDbTestConfigs.config(
                        replicaSet.connectionString,
                        listOf(TEST_DB),
                        extraRootProperties = mapOf("discover_sample_size" to 1000),
                    ),
                )
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName(COLLECTION).withNamespace(TEST_DB),
            )
        MongoClients.create(replicaSet.connectionString).use { client ->
            repeat(ATTEMPTS) { attempt ->
                val byName: Map<String, MongoDbFieldType> =
                    MongoDbSourceMetadataQuerier(config, client).fields(streamId).associate {
                        it.id to it.type as MongoDbFieldType
                    }
                Assertions.assertEquals(
                    MongoDbFieldType.STRING,
                    byName["f"],
                    "attempt $attempt discovered f as ${byName["f"]}",
                )
                Assertions.assertEquals(
                    MongoDbFieldType.NUMBER,
                    byName["n"],
                    "attempt $attempt discovered n as ${byName["n"]}",
                )
                Assertions.assertEquals(MongoDbFieldType.NULL, byName["only_null"])
                Assertions.assertEquals(MongoDbFieldType.STRING, byName["only_string"])
                Assertions.assertEquals(MongoDbFieldType.NUMBER, byName["_id"])
            }
        }
    }

    companion object {
        private const val TEST_DB = "null_vs_string_db"
        private const val COLLECTION = "docs"
        private const val ATTEMPTS = 20

        lateinit var replicaSet: MongoDBContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDBContainer(DockerImageName.parse("mongo:7.0")).also { it.start() }
            MongoClients.create(replicaSet.connectionString).use { client ->
                val coll = client.getDatabase(TEST_DB).getCollection(COLLECTION)
                // Mostly the null shape, plus one document that gives f and n a real type.
                val nulls: List<Document> =
                    (1..40).map { id ->
                        Document("_id", id)
                            .append("f", null)
                            .append("n", null)
                            .append("only_null", null)
                            .append("only_string", "s")
                    }
                val real =
                    Document("_id", 41)
                        .append("f", "hello")
                        .append("n", 7)
                        .append("only_null", null)
                        .append("only_string", "s")
                coll.insertMany(nulls + real)
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }
    }
}
