/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.config

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.MongoCompressor
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

    /**
     * Snappy where the server offers it (cheap for the server, documents compress well), zlib
     * otherwise; a `compressors` connection-string option replaces this, an empty one turns
     * compression off.
     */
    val DEFAULT_COMPRESSORS: List<MongoCompressor> =
        listOf(MongoCompressor.createSnappyCompressor(), MongoCompressor.createZlibCompressor())

    private val COMPRESSORS_OPTION = Regex("[?&]compressors=", RegexOption.IGNORE_CASE)

    fun create(configuration: MongoDbSourceConfiguration): MongoClient =
        MongoClients.create(
            settings(configuration),
            MongoDriverInformation.builder().driverName(DRIVER_NAME).build(),
        )

    /**
     * The client settings [create] uses, built from the configuration and its connection string.
     */
    fun settings(configuration: MongoDbSourceConfiguration): MongoClientSettings {
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
        // The driver parses an absent `compressors` as an empty list, like `compressors=` (none).
        if (!COMPRESSORS_OPTION.containsMatchIn(configuration.connectionString)) {
            settings.compressorList(DEFAULT_COMPRESSORS)
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
        return settings.build()
    }
}
