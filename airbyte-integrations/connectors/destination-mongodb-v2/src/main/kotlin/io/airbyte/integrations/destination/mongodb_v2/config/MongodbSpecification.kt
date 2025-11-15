/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class MongodbSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Connection String")
    @get:JsonPropertyDescription(
        "MongoDB connection string in the format: mongodb://[username:password@]host[:port]/[database][?options]. " +
            "Example: mongodb://user:pass@localhost:27017/mydb or mongodb+srv://cluster.mongodb.net"
    )
    @get:JsonProperty("connection_string")
    @get:JsonSchemaInject(json = """{"order": 0, "airbyte_secret": true}""")
    val connectionString: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database to write to.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 1, "default": "airbyte"}""")
    val database: String = "airbyte"

    @get:JsonSchemaTitle("Authentication Source")
    @get:JsonPropertyDescription(
        "Database where user credentials are stored. Defaults to 'admin'."
    )
    @get:JsonProperty("auth_source")
    @get:JsonSchemaInject(json = """{"order": 2, "default": "admin"}""")
    val authSource: String? = "admin"

    @get:JsonSchemaTitle("Batch Size")
    @get:JsonPropertyDescription(
        "Number of documents to insert in a single batch. Higher values improve performance but use more memory. " +
            "Default: 10,000"
    )
    @get:JsonProperty("batch_size")
    @get:JsonSchemaInject(json = """{"order": 3, "default": 10000, "minimum": 1, "maximum": 100000}""")
    val batchSize: Int? = 10_000
}

@Singleton
class MongodbSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
}
