/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.MongoClients
import com.mongodb.client.model.ChangeStreamPreAndPostImagesOptions
import com.mongodb.client.model.CreateCollectionOptions
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.configuredCatalog
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.read
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport.records
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import java.math.BigDecimal
import java.util.Date
import org.bson.BsonBinary
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.testcontainers.containers.MongoDBContainer

/**
 * The connector against the MongoDB versions it claims to support: a representative document
 * round-trips, a cold start captures a position (`currentPosition()` needs 4.0.7+), the change
 * stream delivers insert/update/delete, and deletes carry a pre-image on 6.0+ but only `_id` before
 * (the stream is opened without `fullDocumentBeforeChange` there).
 */
class MongoDbSourceVersionMatrixTest {

    @ParameterizedTest(name = "{0}")
    @ValueSource(strings = ["mongo:4.4", "mongo:5.0", "mongo:6.0", "mongo:8.0"])
    fun testSnapshotAndChangeStreamOnEveryVersion(image: String) {
        Assumptions.assumeFalse(
            image == "mongo:8.0" && hostKernelAtLeast(6, 19),
            "mongo:8.0 refuses to start on Linux kernel 6.19+ (SERVER-121912)",
        )
        val preImagesSupported: Boolean = image.substringAfter(':').toDouble() >= 6.0
        val container: MongoDBContainer =
            MongoDbReadTestSupport.replicaSet(image).also { it.start() }
        try {
            seed(container, preImagesSupported)
            val config: MongoDbSourceConfigurationSpecification =
                MongoDbReadTestSupport.config(container, listOf(TEST_DB))

            val fullRefresh: BufferingOutputConsumer =
                read(config, configuredCatalog(config, SyncMode.FULL_REFRESH, setOf(PEOPLE)))
            val alice: JsonNode =
                records(fullRefresh, PEOPLE).single { it["name"].asText() == "alice" }
            Assertions.assertEquals("650000000000000000000001", alice["_id"].asText())
            Assertions.assertEquals(30, alice["age"].asInt())
            Assertions.assertEquals(9_007_199_254_740_993L, alice["big"].asLong())
            Assertions.assertEquals(1.5, alice["ratio"].asDouble())
            Assertions.assertEquals(BigDecimal("12.34"), alice["dec"].decimalValue())
            Assertions.assertTrue(alice["active"].asBoolean())
            Assertions.assertEquals("2024-01-01T00:00:00.000Z", alice["created"].asText())
            Assertions.assertEquals("AQID", alice["bin"].asText())
            Assertions.assertEquals(UUID_BASE64, alice["uuid"].asText())
            Assertions.assertEquals("Paris", alice["addr"]["city"].asText())
            Assertions.assertEquals(listOf("a", "b"), alice["tags"].map { it.asText() })
            Assertions.assertTrue(alice["nothing"].isNull)

            val catalog: ConfiguredAirbyteCatalog =
                configuredCatalog(config, SyncMode.INCREMENTAL, setOf(PEOPLE, PRE_IMAGES))
            val sync1: BufferingOutputConsumer = read(config, catalog)
            Assertions.assertEquals(2, records(sync1, PEOPLE).size)
            Assertions.assertEquals(1, records(sync1, PRE_IMAGES).size)

            MongoClients.create(container.connectionString).use { client ->
                val db = client.getDatabase(TEST_DB)
                db.getCollection(PEOPLE)
                    .insertOne(
                        Document("_id", ObjectId("650000000000000000000003"))
                            .append("name", "carol"),
                    )
                db.getCollection(PEOPLE)
                    .updateOne(Filters.eq("name", "alice"), Updates.set("age", 31))
                db.getCollection(PEOPLE).deleteOne(Filters.eq("name", "bob"))
                db.getCollection(PRE_IMAGES).deleteOne(Filters.eq("_id", 1))
            }
            val sync2: BufferingOutputConsumer = read(config, catalog, sync1.states())
            val changes: List<JsonNode> = records(sync2, PEOPLE)
            Assertions.assertEquals(3, changes.size, "insert + update + delete: $changes")
            Assertions.assertEquals(
                "carol",
                changes.single { it["name"]?.asText() == "carol" }["name"].asText(),
            )
            Assertions.assertEquals(
                31,
                changes.single { it["name"]?.asText() == "alice" }["age"].asInt(),
            )
            val deleted: JsonNode = changes.single { !it["_ab_cdc_deleted_at"].isNull }
            Assertions.assertEquals("650000000000000000000002", deleted["_id"].asText())

            val preImageDelete: JsonNode = records(sync2, PRE_IMAGES).single()
            Assertions.assertFalse(preImageDelete["_ab_cdc_deleted_at"].isNull)
            if (preImagesSupported) {
                Assertions.assertEquals(
                    "kept",
                    preImageDelete["name"].asText(),
                    "pre-image on $image",
                )
            } else {
                Assertions.assertTrue(
                    preImageDelete["name"].isNull,
                    "no pre-image before 6.0: $image",
                )
            }
        } finally {
            container.stop()
        }
    }

    private fun seed(container: MongoDBContainer, preImagesSupported: Boolean) {
        MongoClients.create(container.connectionString).use { client ->
            val db = client.getDatabase(TEST_DB)
            db.getCollection(PEOPLE)
                .insertMany(
                    listOf(
                        Document("_id", ObjectId("650000000000000000000001"))
                            .append("name", "alice")
                            .append("age", 30)
                            .append("big", 9_007_199_254_740_993L)
                            .append("ratio", 1.5)
                            .append("dec", Decimal128(BigDecimal("12.34")))
                            .append("active", true)
                            .append("created", Date(1_704_067_200_000L))
                            .append("bin", Binary(byteArrayOf(1, 2, 3)))
                            .append("uuid", Binary(BsonBinary(UUID).type, BsonBinary(UUID).data))
                            .append("addr", Document("city", "Paris"))
                            .append("tags", listOf("a", "b"))
                            .append("nothing", null),
                        Document("_id", ObjectId("650000000000000000000002")).append("name", "bob"),
                    ),
                )
            if (preImagesSupported) {
                db.createCollection(
                    PRE_IMAGES,
                    CreateCollectionOptions()
                        .changeStreamPreAndPostImagesOptions(
                            ChangeStreamPreAndPostImagesOptions(true),
                        ),
                )
            }
            db.getCollection(PRE_IMAGES).insertOne(Document("_id", 1).append("name", "kept"))
        }
    }

    companion object {
        const val TEST_DB = "matrix_db"
        const val PEOPLE = "people"
        const val PRE_IMAGES = "pre_images"
        val UUID: java.util.UUID = java.util.UUID.fromString("123e4567-e89b-12d3-a456-426614174000")
        val UUID_BASE64: String =
            java.util.Base64.getEncoder().encodeToString(BsonBinary(UUID).data)

        /** Containers share the host kernel, so `os.version` is the kernel MongoDB sees. */
        fun hostKernelAtLeast(major: Int, minor: Int): Boolean {
            val (hostMajor: Int, hostMinor: Int) =
                System.getProperty("os.version").split('.', '-').take(2).map { it.toInt() }
            return hostMajor > major || (hostMajor == major && hostMinor >= minor)
        }
    }
}
