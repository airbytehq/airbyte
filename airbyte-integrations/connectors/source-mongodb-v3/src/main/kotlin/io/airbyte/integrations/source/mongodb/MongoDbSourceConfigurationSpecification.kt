/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.fasterxml.jackson.annotation.JsonAnyGetter
import com.fasterxml.jackson.annotation.JsonAnySetter
import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the MongoDb source configuration JSON.
 *
 * Use [MongoDbSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("MongoDb Source Spec")
@JsonPropertyOrder(
    value = ["database_config"],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MongoDbSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "database_config")
    var databaseConfig = MicronautPropertiesFriendlyDatabaseCluster()

    @JsonIgnore var databaseConfigJson: DatabaseClusterType? = null

    @JsonSetter("database_config")
    fun setDatabaseConfigValue(value: DatabaseClusterType) {
        databaseConfigJson = value
    }

    @JsonGetter("database_config")
    @JsonSchemaTitle("Cluster Type")
    @JsonPropertyDescription("Configures the MongoDB cluster type.")
    @JsonSchemaInject(json = """{"order":1,"display_type":"radio"}""")
    fun getDatabaseConfig(): DatabaseClusterType =
        databaseConfigJson ?: databaseConfig.asDatabaseClusterType()

    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds.",
    )
    @JsonSchemaInject(json = """{"order":8, "max": 1200, "min": 120}""")
    var initialWaitTimeInSeconds: Int? = 300

    @JsonProperty("queue_size")
    @JsonSchemaTitle("Size of the queue (Advanced)")
    @JsonPropertyDescription(
        "The size of the internal queue. This may interfere with memory consumption and efficiency of the connector, please be careful."
    )
    @JsonSchemaDefault("10000")
    @JsonSchemaInject(json = """{"order":9}""")
    var queueSize: Int? = 10000

    @JsonProperty("discover_sample_size")
    @JsonSchemaTitle("Document discovery sample size (Advanced)")
    @JsonPropertyDescription(
        "The maximum number of documents to sample when attempting to discover the unique fields for a collection."
    )
    @JsonSchemaDefault("10000")
    @JsonSchemaInject(json = """{"order":10,"maximum": 100000, "minimum": 10}""")
    var discoverSampleSize: Int? = 10000

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC position behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss."
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(json = """{"order":11, "enum": ["Fail sync","Re-sync data"]}""")
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("update_capture_mode")
    @JsonSchemaTitle("Capture mode (Advanced)")
    @JsonPropertyDescription(
        "Determines how Airbyte looks up the value of an updated document. If 'Lookup' is chosen, the current value of the document will be read. If 'Post Image' is chosen, then the version of the document immediately after an update will be read. WARNING : Severe data loss will occur if this option is chosen and the appropriate settings are not set on your Mongo instance : https://www.mongodb.com/docs/manual/changeStreams/#change-streams-with-document-pre-and-post-images."
    )
    @JsonSchemaDefault("Lookup")
    @JsonSchemaInject(json = """{"order":12, "enum": ["Lookup", "Post Image"]}""")
    var updateCaptureMode: String? = "Lookup"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":13, "max": 24, "min": 4}""")
    var initialLoadTimeoutHours: Int? = 8

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

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cluster_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = AtlasReplicaSet::class, name = "ATLAS_REPLICA_SET"),
    JsonSubTypes.Type(value = SelfManagedReplicaSet::class, name = "SELF_MANAGED_REPLICA_SET"),
)
@JsonSchemaTitle("Cluster Type")
@JsonSchemaDescription("Configures the MongoDB cluster type.")
sealed interface DatabaseClusterType

@JsonSchemaTitle("MongoDB Atlas Replica Set")
@JsonSchemaDescription(
    "MongoDB Atlas-hosted cluster configured as a replica set",
)
class AtlasReplicaSet : DatabaseClusterType {
    @JsonProperty("connection_string", required = true)
    @JsonSchemaTitle("Connection String")
    @JsonPropertyDescription(
        "The connection string of the cluster that you want to replicate.",
    )
    @JsonSchemaInject(json = """{"order":2}""")
    var connectionString: String = ""

    @JsonProperty("database", required = true)
    @JsonSchemaTitle("Database Name")
    @JsonPropertyDescription(
        "The name of the MongoDB database that contains the collection(s) to replicate.",
    )
    @JsonSchemaInject(json = """{"order":3}""")
    var database: String = ""

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription(
        "The username which is used to access the database.",
    )
    @JsonSchemaInject(json = """{"order":4}""")
    var username: String = ""

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription(
        "The password associated with this username.",
    )
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret":true}""")
    var password: String = ""

    @JsonProperty("auth_source")
    @JsonSchemaTitle("Authentication Source")
    @JsonPropertyDescription(
        "The authentication source where the user information is stored. See https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authSource for more details.",
    )
    @JsonSchemaInject(json = """{"order":6}""")
    var authSource: String = ""

    @JsonProperty("schema_enforced")
    @JsonSchemaTitle("Schema Enforced")
    @JsonPropertyDescription(
        "When enabled, syncs will validate and structure records against the stream's schema."
    )
    @JsonSchemaInject(json = """{"order":7,"always_show":true}""")
    @JsonSchemaDefault("true")
    var schemaEnforced: Boolean = true
}

@JsonSchemaTitle("Self-Managed Replica Set")
@JsonSchemaDescription("MongoDB self-hosted cluster configured as a replica set")
class SelfManagedReplicaSet : DatabaseClusterType {
    @JsonProperty("connection_string", required = true)
    @JsonSchemaTitle("Connection String")
    @JsonPropertyDescription(
        "The connection string of the cluster that you want to replicate.",
    )
    @JsonSchemaInject(json = """{"order":2}""")
    var connectionString: String = ""

    @JsonProperty("database", required = true)
    @JsonSchemaTitle("Database Name")
    @JsonPropertyDescription(
        "The name of the MongoDB database that contains the collection(s) to replicate.",
    )
    @JsonSchemaInject(json = """{"order":3}""")
    var database: String = ""

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription(
        "The username which is used to access the database.",
    )
    @JsonSchemaInject(json = """{"order":4,"always_show":true}""")
    var username: String? = ""

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription(
        "The password associated with this username.",
    )
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret":true,"always_show":true}""")
    var password: String? = ""

    @JsonProperty("auth_source")
    @JsonSchemaTitle("Authentication Source")
    @JsonPropertyDescription(
        "The authentication source where the user information is stored. See https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authSource for more details.",
    )
    @JsonSchemaInject(json = """{"order":6,"always_show":true}""")
    var authSource: String? = ""

    @JsonProperty("schema_enforced")
    @JsonSchemaTitle("Schema Enforced")
    @JsonPropertyDescription(
        "When enabled, syncs will validate and structure records against the stream's schema."
    )
    @JsonSchemaInject(json = """{"order":7,"always_show":true}""")
    @JsonSchemaDefault("true")
    var schemaEnforced: Boolean = true
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.database_config")
class MicronautPropertiesFriendlyDatabaseCluster {
    var clusterType: String = "ATLAS_REPLICA_SET"

    @JsonValue
    fun asDatabaseClusterType(): DatabaseClusterType =
        when (clusterType) {
            "ATLAS_REPLICA_SET" -> AtlasReplicaSet()
            "SELF_MANAGED_REPLICA_SET" -> SelfManagedReplicaSet()
            else -> throw ConfigErrorException("invalid value $clusterType")
        }
}
