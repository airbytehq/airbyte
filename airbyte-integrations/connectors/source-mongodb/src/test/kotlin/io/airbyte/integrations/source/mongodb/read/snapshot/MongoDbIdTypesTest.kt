/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.snapshot

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import java.util.Date
import org.bson.Document
import org.bson.types.Code
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer

/** [MongoDbIdTypes.present] against a live replica set: the legacy connector's `_id` type probe. */
class MongoDbIdTypesTest {

    @Test
    fun testEmptyCollectionHasNoTypes() {
        Assertions.assertEquals(emptyList<String>(), MongoDbIdTypes.present(collection("empty")))
    }

    @Test
    fun testOneTypeIsPinnedByTheIndexEndpoints() {
        Assertions.assertEquals(
            listOf("objectId"),
            MongoDbIdTypes.present(seeded("object_ids", (1..3).map { ObjectId() })),
        )
        Assertions.assertEquals(
            listOf("string"),
            MongoDbIdTypes.present(seeded("strings", listOf("a", "b"))),
        )
    }

    /** Every numeric width is the one type `number`, as it is for the resume comparison. */
    @Test
    fun testNumericWidthsAreOneType() {
        val ids: List<Any> = listOf(1, 2.5, 5_000_000_000L, Decimal128.parse("7000000000.5"))
        Assertions.assertEquals(listOf("number"), MongoDbIdTypes.present(seeded("numbers", ids)))
    }

    /** Members of one bracket interleave in the index and are probed one by one. */
    @Test
    fun testStringAndSymbolShareABracket() {
        val ids: List<Any> = listOf("a", org.bson.types.Symbol("s"), "z")
        Assertions.assertEquals(
            listOf("string", "symbol"),
            MongoDbIdTypes.present(seeded("string_symbol", ids)),
        )
    }

    /** `_id`s spanning brackets: every candidate type is probed, in index order. */
    @Test
    fun testMixedBracketsListEveryTypePresent() {
        val ids: List<Any> =
            listOf(1, "two", Date(1_700_000_000_000L), ObjectId(), Code("function f() {}"), true)
        Assertions.assertEquals(
            listOf("number", "string", "objectId", "bool", "date", "javascript"),
            MongoDbIdTypes.present(seeded("mixed", ids)),
        )
    }

    private fun collection(name: String): MongoCollection<Document> =
        client.getDatabase(TEST_DB).getCollection(name)

    private fun seeded(name: String, ids: List<Any>): MongoCollection<Document> =
        collection(name).also { coll ->
            coll.drop()
            coll.insertMany(ids.map { Document("_id", it) })
        }

    companion object {
        const val TEST_DB = "id_types_db"

        lateinit var replicaSet: MongoDBContainer
        lateinit var client: MongoClient

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
            client = MongoClients.create(replicaSet.connectionString)
            client.getDatabase(TEST_DB).createCollection("empty")
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            client.close()
            replicaSet.stop()
        }
    }
}
