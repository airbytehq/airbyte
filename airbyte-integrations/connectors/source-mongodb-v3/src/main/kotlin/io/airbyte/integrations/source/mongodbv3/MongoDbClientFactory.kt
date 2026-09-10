/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.MongoCredential
import com.mongodb.MongoDriverInformation
import com.mongodb.ReadPreference
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

/**
 * Builds a [MongoClient] from a [MongoDbSourceConfiguration], the same way the legacy connector
 * did.
 */
object MongoDbClientFactory {
    const val DRIVER_NAME = "Airbyte"

    fun create(configuration: MongoDbSourceConfiguration): MongoClient {
        val connectionString = ConnectionString(configuration.connectionString)
        val settings: MongoClientSettings.Builder =
            MongoClientSettings.builder().applyConnectionString(connectionString)
        if (connectionString.readPreference == null) {
            settings.readPreference(ReadPreference.secondaryPreferred())
        }
        if (configuration.hasCredentials) {
            // The legacy connector URL-encodes the username before handing it to the driver;
            // kept as-is for parity.
            val username: String = URLEncoder.encode(configuration.username, StandardCharsets.UTF_8)
            settings.credential(
                MongoCredential.createCredential(
                    username,
                    configuration.authSource,
                    configuration.password!!.toCharArray(),
                ),
            )
        }
        val driverInformation: MongoDriverInformation =
            MongoDriverInformation.builder().driverName(DRIVER_NAME).build()
        return MongoClients.create(settings.build(), driverInformation)
    }
}
