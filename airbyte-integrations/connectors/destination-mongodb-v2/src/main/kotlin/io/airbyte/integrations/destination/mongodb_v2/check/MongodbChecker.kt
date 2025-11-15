/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.check

import com.mongodb.kotlin.client.coroutine.MongoClient
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbConfiguration
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking
import org.bson.Document
import java.time.Clock

@Singleton
class MongodbChecker(
    clock: Clock,
    private val client: MongoClient,
) : DestinationChecker<MongodbConfiguration> {
    @VisibleForTesting val collectionName = "_airbyte_check_collection_${clock.millis()}"

    override fun check(config: MongodbConfiguration) = runBlocking {
        val database = client.getDatabase(config.resolvedDatabase)
        val collection = database.getCollection<Document>(collectionName)

        // Create collection and insert a test document
        val testDoc = Document("test", 42)
        collection.insertOne(testDoc)

        // Verify we can read it back
        val count = collection.countDocuments()
        require(count == 1L) {
            "Failed to insert and read test document. Expected 1 document, found $count"
        }
    }

    override fun cleanup(config: MongodbConfiguration) = runBlocking {
        val database = client.getDatabase(config.resolvedDatabase)
        database.getCollection<Document>(collectionName).drop()
    }
}
