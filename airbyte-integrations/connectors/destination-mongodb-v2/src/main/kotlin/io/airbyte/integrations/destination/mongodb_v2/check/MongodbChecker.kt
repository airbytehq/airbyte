/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.check

import com.mongodb.client.MongoClient
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.integrations.destination.mongodb_v2.client.MongodbAirbyteClient
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking
import org.bson.Document

private val log = KotlinLogging.logger {}

@Singleton
class MongodbChecker(
    private val mongoClient: MongoClient,
    private val config: MongodbConfiguration,
    private val mongodbClient: MongodbAirbyteClient,
) : DestinationCheckerV2 {

    override fun check() {
        runBlocking {
            try {
                // Test 1: Can we connect to MongoDB?
                val databases = mongoClient.listDatabaseNames().into(mutableListOf())
                log.info { "Successfully connected to MongoDB. Found ${databases.size} databases." }

                // Test 2: Does the target database exist or can we create it?
                val database = mongoClient.getDatabase(config.database)

                // Test 3: Can we create a test collection?
                val testCollectionName = "_airbyte_connection_test_${System.currentTimeMillis()}"

                try {
                    database.createCollection(testCollectionName)
                    log.info { "Successfully created test collection: $testCollectionName" }

                    // Test 4: Can we insert a document?
                    val testCollection = database.getCollection(testCollectionName)
                    val testDoc = Document("test", "data")
                        .append("timestamp", System.currentTimeMillis())

                    testCollection.insertOne(testDoc)
                    log.info { "Successfully inserted test document" }

                    // Test 5: Can we read the document back?
                    val count = testCollection.countDocuments()
                    require(count == 1L) {
                        "Expected 1 document in test collection, found $count"
                    }
                    log.info { "Successfully read test document" }

                } finally {
                    // Clean up test collection
                    database.getCollection(testCollectionName).drop()
                    log.info { "Cleaned up test collection: $testCollectionName" }
                }

                log.info { "Connection check passed successfully" }

            } catch (e: Exception) {
                log.error(e) { "Connection check failed" }
                throw ConfigErrorException(
                    "Failed to connect to MongoDB or perform operations. " +
                    "Please verify your connection string, credentials, and permissions.\n\n" +
                    "Error: ${e.message}",
                    e
                )
            }
        }
    }
}
