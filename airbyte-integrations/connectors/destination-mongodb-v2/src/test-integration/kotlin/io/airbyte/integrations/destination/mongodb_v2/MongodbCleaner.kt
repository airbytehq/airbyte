/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import com.mongodb.kotlin.client.coroutine.MongoClient
import io.airbyte.cdk.load.test.util.DestinationCleaner
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

class MongodbCleaner(
    private val mongoClient: MongoClient,
    private val testNamespace: String = "test",
) : DestinationCleaner {

    override fun cleanup() = runBlocking {
        try {
            val database = mongoClient.getDatabase(testNamespace)

            // List all collections in the test database
            val collectionNames = database.listCollectionNames().toList()

            // Drop each collection
            collectionNames.forEach { collectionName ->
                try {
                    database.getCollection<org.bson.Document>(collectionName).drop()
                } catch (e: Exception) {
                    // Ignore errors during cleanup
                }
            }

            // Drop the database itself
            try {
                database.drop()
            } catch (e: Exception) {
                // Ignore errors during cleanup
            }
        } catch (e: Exception) {
            // Ignore all errors during cleanup
        }
    }
}
