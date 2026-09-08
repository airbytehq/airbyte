/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

/**
 * The object which is mapped to the MongoDB source configuration JSON.
 *
 * Property names, titles, descriptions, defaults and ordering deliberately mirror the legacy
 * `source-mongodb-v2` `spec.json`, so that saved configurations keep deserializing and the `spec`
 * output stays identical. Use [MongoDbSourceConfiguration] instead wherever possible.
 */
@JsonSchemaTitle("MongoDb Source Spec")
@JsonSchemaInject(
    json = """{"groups":[{"id":"connection"},{"id":"advanced","title":"Advanced"}]}""",
)
@JsonPropertyOrder(
    value =
        [
            "database_config",
            "initial_waiting_seconds",
            "queue_size",
            "discover_sample_size",
            "discover_timeout_seconds",
            "invalid_cdc_cursor_position_behavior",
            "update_capture_mode",
            "initial_load_timeout_hours",
        ],
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MongoDbSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("database_config")
    @JsonSchemaTitle("Cluster Type")
    @JsonSchemaDescription("Configures the MongoDB cluster type.")
    @JsonSchemaInject(json = """{"order":1,"group":"connection","display_type":"radio"}""")
    lateinit var databaseConfig: DatabaseConfigSpecification

    /** Null when the (required) `database_config` property is absent from the config JSON. */
    fun databaseConfigOrNull(): DatabaseConfigSpecification? =
        if (this::databaseConfig.isInitialized) databaseConfig else null

    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonSchemaDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds.",
    )
    @JsonSchemaInject(
        json = """{"default":300,"order":8,"min":120,"max":1200,"group":"advanced"}"""
    )
    var initialWaitingSeconds: Int? = DEFAULT_INITIAL_WAITING_SECONDS

    @JsonProperty("queue_size")
    @JsonSchemaTitle("Size of the queue (Advanced)")
    @JsonSchemaDescription(
        "The size of the internal queue. This may interfere with memory consumption and efficiency of the connector, please be careful.",
    )
    @JsonSchemaInject(
        json = """{"default":10000,"order":9,"min":1000,"max":10000,"group":"advanced"}""",
    )
    var queueSize: Int? = DEFAULT_QUEUE_SIZE

    @JsonProperty("discover_sample_size")
    @JsonSchemaTitle("Document discovery sample size (Advanced)")
    @JsonSchemaDescription(
        "The maximum number of documents to sample when attempting to discover the unique fields for a collection.",
    )
    @JsonSchemaInject(
        json = """{"default":10000,"order":10,"minimum":10,"maximum":100000,"group":"advanced"}""",
    )
    var discoverSampleSize: Int? = DEFAULT_DISCOVER_SAMPLE_SIZE

    @JsonProperty("discover_timeout_seconds")
    @JsonSchemaTitle("Document discovery timeout in seconds (Advanced)")
    @JsonSchemaDescription(
        "The amount of time the connector will wait when it discovers a document. Defaults to 600 seconds. Valid range: 5 seconds to 1200 seconds.",
    )
    @JsonSchemaInject(
        json = """{"default":600,"order":11,"minimum":5,"maximum":1200,"group":"advanced"}""",
    )
    var discoverTimeoutSeconds: Int? = DEFAULT_DISCOVER_TIMEOUT_SECONDS

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC position behavior (Advanced)")
    @JsonSchemaDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.",
    )
    @JsonSchemaInject(
        json =
            """{"enum":["Fail sync","Re-sync data"],"default":"Fail sync","order":12,"group":"advanced"}""",
    )
    var invalidCdcCursorPositionBehavior: String? =
        InvalidCdcCursorPositionBehavior.FAIL_SYNC.specValue

    @JsonProperty("update_capture_mode")
    @JsonSchemaTitle("Capture mode (Advanced)")
    @JsonSchemaDescription(
        "Determines how Airbyte looks up the value of an updated document. If 'Lookup' is chosen, the current value of the document will be read. If 'Post Image' is chosen, then the version of the document immediately after an update will be read. WARNING : Severe data loss will occur if this option is chosen and the appropriate settings are not set on your Mongo instance : https://www.mongodb.com/docs/manual/changeStreams/#change-streams-with-document-pre-and-post-images.",
    )
    @JsonSchemaInject(
        json =
            """{"enum":["Lookup","Post Image"],"default":"Lookup","order":13,"group":"advanced"}""",
    )
    var updateCaptureMode: String? = UpdateCaptureMode.LOOKUP.specValue

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonSchemaDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs.",
    )
    @JsonSchemaInject(json = """{"default":8,"min":4,"max":24,"order":14,"group":"advanced"}""")
    var initialLoadTimeoutHours: Int? = DEFAULT_INITIAL_LOAD_TIMEOUT_HOURS

    companion object {
        const val DEFAULT_INITIAL_WAITING_SECONDS = 300
        const val DEFAULT_QUEUE_SIZE = 10_000
        const val DEFAULT_DISCOVER_SAMPLE_SIZE = 10_000
        const val DEFAULT_DISCOVER_TIMEOUT_SECONDS = 600
        const val DEFAULT_INITIAL_LOAD_TIMEOUT_HOURS = 8
        const val DEFAULT_AUTH_SOURCE = "admin"
    }
}

/**
 * The `database_config` oneOf. Both variants carry the same connection properties; the Atlas
 * variant additionally requires credentials. The `cluster_type` discriminator is synthesized by
 * Jackson; [MongoDbSpecificationExtender] renders it as `const` like the legacy spec does.
 */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = DatabaseConfigSpecification.CLUSTER_TYPE)
@JsonSubTypes(
    JsonSubTypes.Type(value = AtlasReplicaSetSpecification::class, name = "ATLAS_REPLICA_SET"),
    JsonSubTypes.Type(
        value = SelfManagedReplicaSetSpecification::class,
        name = "SELF_MANAGED_REPLICA_SET",
    ),
)
@JsonSchemaTitle("Cluster Type")
@JsonSchemaDescription("Configures the MongoDB cluster type.")
sealed interface DatabaseConfigSpecification {
    val connectionString: String
    val databases: List<String>
    val username: String?
    val password: String?
    val authSource: String?
    val schemaEnforced: Boolean?

    companion object {
        const val CLUSTER_TYPE = "cluster_type"
    }
}

@JsonSchemaTitle("MongoDB Atlas Replica Set")
@JsonSchemaDescription("MongoDB Atlas-hosted cluster configured as a replica set")
@JsonPropertyOrder(
    value =
        [
            "connection_string",
            "databases",
            "username",
            "password",
            "auth_source",
            "schema_enforced",
        ],
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class AtlasReplicaSetSpecification : DatabaseConfigSpecification {
    @JsonProperty("connection_string")
    @JsonSchemaTitle("Connection String")
    @JsonSchemaDescription("The connection string of the cluster that you want to replicate.")
    @JsonSchemaInject(
        json = """{"examples":["mongodb+srv://cluster0.abcd1.mongodb.net/"],"order":2}""",
    )
    override lateinit var connectionString: String

    @JsonProperty("databases")
    @JsonSchemaTitle("Database Names")
    @JsonSchemaDescription(
        "The names of the MongoDB databases that contain the collection(s) to replicate.",
    )
    @JsonSchemaInject(json = """{"order":3}""")
    override lateinit var databases: List<String>

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonSchemaDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    override lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonSchemaDescription("The password associated with this username.")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"order":5}""")
    override lateinit var password: String

    @JsonProperty("auth_source")
    @JsonSchemaTitle("Authentication Source")
    @JsonSchemaDescription(
        "The authentication source where the user information is stored.  See https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.authSource for more details.",
    )
    @JsonSchemaInject(json = """{"default":"admin","examples":["admin"],"order":6}""")
    override var authSource: String = MongoDbSourceConfigurationSpecification.DEFAULT_AUTH_SOURCE

    @JsonProperty("schema_enforced")
    @JsonSchemaTitle("Schema Enforced")
    @JsonSchemaDescription(
        "When enabled, syncs will validate and structure records against the stream's schema.",
    )
    @JsonSchemaInject(json = """{"default":true,"always_show":true,"order":7}""")
    override var schemaEnforced: Boolean? = true
}

@JsonSchemaTitle("Self-Managed Replica Set")
@JsonSchemaDescription("MongoDB self-hosted cluster configured as a replica set")
@JsonPropertyOrder(
    value =
        [
            "connection_string",
            "databases",
            "username",
            "password",
            "auth_source",
            "schema_enforced",
        ],
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SelfManagedReplicaSetSpecification : DatabaseConfigSpecification {
    @JsonProperty("connection_string")
    @JsonSchemaTitle("Connection String")
    @JsonSchemaDescription(
        "The connection string of the cluster that you want to replicate.  https://www.mongodb.com/docs/manual/reference/connection-string/#find-your-self-hosted-deployment-s-connection-string for more information.",
    )
    @JsonSchemaInject(
        json =
            """{"examples":["mongodb://example1.host.com:27017,example2.host.com:27017,example3.host.com:27017/","mongodb://example.host.com:27017/"],"order":2}""",
    )
    override lateinit var connectionString: String

    @JsonProperty("databases")
    @JsonSchemaTitle("Database Names")
    @JsonSchemaDescription(
        "The names of the MongoDB databases that contain the collection(s) to replicate.",
    )
    @JsonSchemaInject(json = """{"order":3}""")
    override lateinit var databases: List<String>

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonSchemaDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    override var username: String? = null

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonSchemaDescription("The password associated with this username.")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"order":5}""")
    override var password: String? = null

    @JsonProperty("auth_source")
    @JsonSchemaTitle("Authentication Source")
    @JsonSchemaDescription("The authentication source where the user information is stored.")
    @JsonSchemaInject(json = """{"default":"admin","examples":["admin"],"order":6}""")
    override var authSource: String? = MongoDbSourceConfigurationSpecification.DEFAULT_AUTH_SOURCE

    @JsonProperty("schema_enforced")
    @JsonSchemaTitle("Schema Enforced")
    @JsonSchemaDescription(
        "When enabled, syncs will validate and structure records against the stream's schema.",
    )
    @JsonSchemaInject(json = """{"default":true,"always_show":true,"order":7}""")
    override var schemaEnforced: Boolean? = true
}
