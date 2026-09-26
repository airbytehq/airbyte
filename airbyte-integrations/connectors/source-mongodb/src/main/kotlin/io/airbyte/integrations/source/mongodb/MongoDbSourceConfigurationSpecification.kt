/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.annotation.JsonAnyGetter
import com.fasterxml.jackson.annotation.JsonAnySetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the MongoDB source configuration JSON.
 *
 * Use [MongoDbSourceConfiguration] instead wherever possible.
 */
@JsonSchemaTitle("MongoDB Source Spec")
@JsonPropertyOrder(
    value = ["connection_string", "database", "username", "password", "auth_source"],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MongoDbSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("connection_string")
    @JsonSchemaTitle("Connection String")
    @JsonPropertyDescription(
        "The MongoDB connection string. " +
            "For MongoDB Atlas, this should be in the format: " +
            "mongodb+srv://<cluster-url>/<options>. " +
            "For self-hosted MongoDB, use: mongodb://<host>:<port>/<options>. " +
            "Do not include credentials in the connection string; use the username and password fields instead."
    )
    @JsonSchemaInject(json = """{"order":1}""")
    lateinit var connectionString: String

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The name of the MongoDB database to sync from.")
    @JsonSchemaInject(json = """{"order":2}""")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username used to authenticate with MongoDB.")
    @JsonSchemaInject(json = """{"order":3}""")
    var username: String? = null

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":4,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("auth_source")
    @JsonSchemaTitle("Auth Source")
    @JsonPropertyDescription(
        "The database used for authentication. " +
            "Defaults to 'admin' if not specified."
    )
    @JsonSchemaInject(json = """{"order":5}""")
    @JsonSchemaDefault("admin")
    var authSource: String = "admin"

    @JsonProperty("discover_sample_size")
    @JsonSchemaTitle("Schema Discovery Sample Size")
    @JsonPropertyDescription(
        "The maximum number of documents to sample when discovering the schema. " +
            "Larger values may provide more accurate schema discovery but will take longer."
    )
    @JsonSchemaInject(json = """{"order":6}""")
    @JsonSchemaDefault("10000")
    var discoverSampleSize: Int = 10000

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":7}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaInject(json = """{"order":8}""")
    @JsonSchemaDefault("1")
    @JsonPropertyDescription("Maximum number of concurrent queries to the database.")
    var concurrency: Int = 1

    @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnyGetter fun getAdditionalProperties(): Map<String, Any> = additionalPropertiesMap

    @JsonAnySetter
    fun setAdditionalProperty(
        name: String,
        value: Any,
    ) {
        additionalPropertiesMap[name] = value
    }
}
