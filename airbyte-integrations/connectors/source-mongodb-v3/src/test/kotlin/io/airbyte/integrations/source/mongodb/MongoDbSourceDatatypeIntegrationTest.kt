/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoDatabase
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteStream
import kotlin.test.assertEquals
import org.bson.Document
import org.junit.jupiter.api.Test

class MongoDbSourceDatatypeIntegrationTest {
    @Test
    fun testDiscover() {
        insertDocument(
            dbContainer.connectionString,
            "test",
            "test",
            Document("name", "John Doe").append("age", 32).append("occupation", "Engineer")
        )

        val actualStreams: Map<String, AirbyteStream> by lazy {
            val output: BufferingOutputConsumer = CliRunner.source("discover", config()).run()
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        }

        assertEquals(1, actualStreams.size)
        val actualStream = actualStreams["test"]
        assertEquals("test", actualStream?.name)
        val jsonSchema = actualStream?.jsonSchema
        assertEquals(
            "string",
            jsonSchema?.get("properties")?.get("occupation")?.get("type")?.asText()
        )
        assertEquals("number", jsonSchema?.get("properties")?.get("age")?.get("type")?.asText())
        assertEquals("string", jsonSchema?.get("properties")?.get("name")?.get("type")?.asText())
        assertEquals("string", jsonSchema?.get("properties")?.get("_id")?.get("type")?.asText())
    }

    fun insertDocument(
        connectionString: String,
        databaseName: String,
        collectionName: String,
        document: Document
    ) {
        val mongoClient: MongoClient = MongoClients.create(connectionString)
        val database: MongoDatabase = mongoClient.getDatabase(databaseName)
        val collection: MongoCollection<Document> = database.getCollection(collectionName)
        collection.insertOne(document)
    }

    companion object {
        var dbContainer: org.testcontainers.containers.MongoDBContainer =
            MongoDbContainerFactory.shared("mongo:4.0.10")

        fun config(): MongoDbSourceConfigurationSpecification =
            MongoDbContainerFactory.config(dbContainer)
    }
}
