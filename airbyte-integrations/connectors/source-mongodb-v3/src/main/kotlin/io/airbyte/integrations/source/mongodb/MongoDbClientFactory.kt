/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.MongoDriverInformation
import com.mongodb.ReadPreference
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import javax.inject.Singleton

@Singleton
class MongoDbClientFactory {
    companion object {
        private const val DRIVER_NAME: String = "Airbyte"
    }

    fun make(config: MongoDbSourceConfiguration): MongoClient {
        val mongoDriverInformation =
            MongoDriverInformation.builder().driverName(DRIVER_NAME).build()

        val mongoClientSettingsBuilder =
            MongoClientSettings.builder()
                .applyConnectionString(ConnectionString(config.connectionString))
                .readPreference(ReadPreference.secondaryPreferred())

        if (config.mongoCredential != null) {
            mongoClientSettingsBuilder.credential(config.mongoCredential)
        }

        return MongoClients.create(mongoClientSettingsBuilder.build(), mongoDriverInformation)
    }
}
