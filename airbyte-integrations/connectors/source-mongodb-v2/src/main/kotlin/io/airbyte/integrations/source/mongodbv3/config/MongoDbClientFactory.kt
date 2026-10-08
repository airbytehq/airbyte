/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.config

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.MongoCredential
import com.mongodb.MongoDriverInformation
import com.mongodb.ReadPreference
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import org.bson.UuidRepresentation

/** Builds a [MongoClient] from a [MongoDbSourceConfiguration]. */
object MongoDbClientFactory {
    const val DRIVER_NAME = "Airbyte"

    fun create(configuration: MongoDbSourceConfiguration): MongoClient {
        val connectionString = ConnectionString(configuration.connectionString)
        val settings: MongoClientSettings.Builder =
            MongoClientSettings.builder()
                .applyConnectionString(connectionString)
                // Binary values are emitted as their raw bytes whatever their subtype; a UUID
                // representation (also settable in the connection string) would decode subtype 3/4
                // binaries to `UUID` objects and lose the subtype the `_id` checkpoint needs.
                .uuidRepresentation(UuidRepresentation.UNSPECIFIED)
        if (connectionString.readPreference == null) {
            settings.readPreference(ReadPreference.secondaryPreferred())
        }
        // Atlas requires TLS; self-managed clusters honour the connection string (`tls=true`).
        if (configuration.clusterType == MongoDbClusterType.ATLAS_REPLICA_SET) {
            settings.applyToSslSettings { it.enabled(true) }
        }
        configuration.credential?.let { (username: String, password: String) ->
            // The username is URL-encoded before it is handed to the driver.
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
