/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoDatabase
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteCatalog
import java.math.BigDecimal
import java.util.Date
import java.util.UUID
import org.bson.BsonBinarySubType
import org.bson.BsonRegularExpression
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Code
import org.bson.types.CodeWithScope
import org.bson.types.Decimal128
import org.bson.types.MaxKey
import org.bson.types.MinKey
import org.bson.types.ObjectId
import org.bson.types.Symbol
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

/**
 * Runs DISCOVER against a seeded replica set and compares the catalog with the one the legacy
 * `airbyte/source-mongodb-v2` image produced for the same data (`expected-catalog-*.json`).
 *
 * The seed covers every BSON type, an empty collection (omitted from the catalog), a view
 * (included), a `system.*` collection (omitted), several `_id` types and a second database.
 */
class MongoDbSourceDiscoverTest {

    @Test
    fun testDiscoverSchemaEnforced() {
        assertCatalogMatchesLegacy(
            MongoDbSourceCheckTest.config(replicaSet.connectionString, listOf(TEST_DB)),
            "expected-catalog-schema-enforced.json",
        )
    }

    @Test
    fun testDiscoverSchemaless() {
        assertCatalogMatchesLegacy(
            MongoDbSourceCheckTest.config(
                replicaSet.connectionString,
                listOf(TEST_DB),
                schemaEnforced = false
            ),
            "expected-catalog-schemaless.json",
        )
    }

    @Test
    fun testDiscoverMultipleDatabases() {
        assertCatalogMatchesLegacy(
            MongoDbSourceCheckTest.config(replicaSet.connectionString, listOf(TEST_DB, OTHER_DB)),
            "expected-catalog-multi-db.json",
        )
    }

    @Test
    fun testDiscoverIgnoresUnreadableDatabase() {
        assertCatalogMatchesLegacy(
            MongoDbSourceCheckTest.config(
                replicaSet.connectionString,
                listOf("does_not_exist", TEST_DB)
            ),
            "expected-catalog-schema-enforced.json",
        )
    }

    private fun assertCatalogMatchesLegacy(
        config: MongoDbSourceConfigurationSpecification,
        expectedCatalogResource: String,
    ) {
        val expected: JsonNode =
            normalize(Jsons.readTree(ResourceUtils.readResource(expectedCatalogResource)))
        val catalogs: List<AirbyteCatalog> = CliRunner.source("discover", config).run().catalogs()
        Assertions.assertEquals(1, catalogs.size)
        val actual: JsonNode = normalize(Jsons.valueToTree(catalogs.first()))
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual)
        )
    }

    /**
     * Stream order is not significant (the legacy connector emitted streams in `HashSet` order) and
     * neither is JSON object key order, which [JsonNode.equals] already ignores.
     */
    private fun normalize(catalog: JsonNode): JsonNode {
        val streams: ArrayNode = catalog["streams"] as ArrayNode
        val sorted: List<JsonNode> =
            streams.sortedBy { "${it["namespace"].asText()}.${it["name"].asText()}" }
        return (catalog.deepCopy<ObjectNode>()).apply {
            set<JsonNode>("streams", Jsons.arrayNode().addAll(sorted))
        }
    }

    companion object {
        const val TEST_DB = "test_db"
        const val OTHER_DB = "other_db"

        lateinit var replicaSet: MongoDBContainer

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

        /** Same data as the legacy parity harness (`seed.js`), so the expected catalogs apply. */
        fun seed(client: MongoClient) {
            val testDb: MongoDatabase = client.getDatabase(TEST_DB)
            testDb
                .getCollection("people")
                .insertMany(
                    listOf(
                        Document("_id", ObjectId("650000000000000000000001"))
                            .append("name", "alice")
                            .append("age", 30)
                            .append("active", true)
                            .append("score", 1.5)
                            .append("created", Date(1704067200000L))
                            .append("tags", listOf("a", "b"))
                            .append("address", Document("city", "Paris").append("zip", "75001"))
                            .append("nothing", null)
                            .append("big", 9007199254740993L)
                            .append("dec", Decimal128(BigDecimal("12.34")))
                            .append(
                                "uuid",
                                uuidBinary(UUID.fromString("123e4567-e89b-12d3-a456-426614174000"))
                            )
                            .append("bin", Binary(byteArrayOf(1, 2, 3)))
                            .append("ts", BsonTimestamp(1700000000, 1))
                            .append("re", BsonRegularExpression("abc", "i"))
                            .append("code", Code("function(){}"))
                            .append("codews", CodeWithScope("function(){}", Document("x", 1)))
                            .append("sym", Symbol("sym"))
                            .append("minK", MinKey())
                            .append("maxK", MaxKey()),
                        Document("_id", ObjectId("650000000000000000000002"))
                            .append("name", "bob")
                            .append("age", 41)
                            .append("active", false)
                            .append("score", 2.5)
                            .append("created", Date(1706745600000L))
                            .append("tags", emptyList<String>())
                            .append("address", Document("city", "Berlin"))
                            .append("nothing", null)
                            .append("big", 1L)
                            .append("dec", Decimal128(BigDecimal("0.1")))
                            .append(
                                "uuid",
                                uuidBinary(UUID.fromString("223e4567-e89b-12d3-a456-426614174000"))
                            )
                            .append("bin", Binary(byteArrayOf(4, 5, 6)))
                            .append("ts", BsonTimestamp(1700000001, 1))
                            .append("re", BsonRegularExpression("def"))
                            .append("code", Code("function(){return 1}"))
                            .append("codews", CodeWithScope("function(){}", Document("y", 2)))
                            .append("sym", Symbol("sym2"))
                            .append("minK", MinKey())
                            .append("maxK", MaxKey()),
                        Document("_id", ObjectId("650000000000000000000003"))
                            .append("name", "carol")
                            .append("extra_only_here", "x"),
                    ),
                )
            testDb
                .getCollection("int_id")
                .insertMany(
                    listOf(
                        Document("_id", 1).append("v", "one"),
                        Document("_id", 2).append("v", "two")
                    )
                )
            testDb
                .getCollection("string_id")
                .insertMany(
                    listOf(
                        Document("_id", "k1").append("v", 1),
                        Document("_id", "k2").append("v", 2)
                    )
                )
            testDb.createCollection("empty_coll")
            testDb.createView(
                "people_view",
                "people",
                listOf(Document("\$project", Document("name", 1)))
            )
            testDb.createCollection("system.buckets.ignored")
            client
                .getDatabase(OTHER_DB)
                .getCollection("orders")
                .insertOne(
                    Document("_id", ObjectId("660000000000000000000001"))
                        .append("total", 10)
                        .append("items", listOf(Document("sku", "a"))),
                )
        }

        private fun uuidBinary(uuid: UUID): Binary {
            val bytes =
                java.nio.ByteBuffer.allocate(16)
                    .putLong(uuid.mostSignificantBits)
                    .putLong(uuid.leastSignificantBits)
                    .array()
            return Binary(BsonBinarySubType.UUID_STANDARD, bytes)
        }
    }
}
