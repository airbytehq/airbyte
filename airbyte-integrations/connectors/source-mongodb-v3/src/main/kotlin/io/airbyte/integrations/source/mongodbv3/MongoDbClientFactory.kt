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
        configuration.credential?.let { (username: String, password: String) ->
            // The legacy connector URL-encodes the username before handing it to the driver;
            // kept as-is for parity.
            settings.credential(
                MongoCredential.createCredential(
                    URLEncoder.encode(username, StandardCharsets.UTF_8),
                    configuration.authSource,
                    password.toCharArray(),
                ),
            )
        }
        val driverInformation: MongoDriverInformation =
            MongoDriverInformation.builder().driverName(DRIVER_NAME).build()
        return MongoClients.create(settings.build(), driverInformation)
    }
}
