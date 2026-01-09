/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

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
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the PostgreSQL source configuration JSON.
 *
 * Use [PostgresV2SourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("PostgreSQL V2 Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "database",
            "schemas",
            "username",
            "password",
            "ssl_mode",
            "replication_method"
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class PostgresV2SourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription("Hostname of the database.")
    @JsonSchemaInject(json = """{"order":1}""")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("5432")
    @JsonPropertyDescription("Port of the database.")
    var port: Int = 5432

    @JsonProperty("database")
    @JsonSchemaTitle("Database Name")
    @JsonPropertyDescription("Name of the database.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonPropertyDescription(
        "The list of schemas (case sensitive) to sync from. Defaults to public."
    )
    @JsonSchemaInject(json = """{"order":4,"minItems":1,"uniqueItems":true}""")
    @JsonSchemaDefault("[\"public\"]")
    var schemas: List<String> = listOf("public")

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":5}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":6,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Parameters")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3)."
    )
    @JsonSchemaInject(json = """{"order":7}""")
    var jdbcUrlParams: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "ssl_mode")
    var sslMode = MicronautPropertiesFriendlySslModeSpecification()

    @JsonIgnore var sslModeJson: SslModeSpecification? = null

    @JsonSetter("ssl_mode")
    fun setSslModeValue(value: SslModeSpecification) {
        sslModeJson = value
    }

    @JsonGetter("ssl_mode")
    @JsonSchemaTitle("SSL Modes")
    @JsonPropertyDescription(
        "SSL connection modes. " +
            "Read more in the <a href=\"https://jdbc.postgresql.org/documentation/ssl/\">PostgreSQL documentation</a>."
    )
    @JsonSchemaInject(json = """{"order":8}""")
    fun getSslModeValue(): SslModeSpecification? = sslModeJson ?: sslMode.asSslMode()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, " +
            "and if so, which kind of authentication to use."
    )
    @JsonSchemaInject(json = """{"order":9}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "replication_method")
    var replicationMethod = MicronautPropertiesFriendlyIncrementalConfigurationSpecification()

    @JsonIgnore var replicationMethodJson: IncrementalConfigurationSpecification? = null

    @JsonSetter("replication_method")
    fun setIncrementalValue(value: IncrementalConfigurationSpecification) {
        replicationMethodJson = value
    }

    @JsonGetter("replication_method")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getIncrementalValue(): IncrementalConfigurationSpecification =
        replicationMethodJson ?: replicationMethod.asIncrementalConfiguration()

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":11}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaInject(json = """{"order":12,"airbyte_hidden":true}""")
    @JsonSchemaDefault("1")
    @JsonPropertyDescription("Maximum number of concurrent queries to the database.")
    var concurrency: Int? = 1

    @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnyGetter fun getAdditionalProperties(): Map<String, Any> = additionalPropertiesMap

    @JsonAnySetter
    fun setAdditionalProperty(name: String, value: Any) {
        additionalPropertiesMap[name] = value
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(value = SslModeDisable::class, name = "disable"),
    JsonSubTypes.Type(value = SslModeAllow::class, name = "allow"),
    JsonSubTypes.Type(value = SslModePrefer::class, name = "prefer"),
    JsonSubTypes.Type(value = SslModeRequire::class, name = "require"),
    JsonSubTypes.Type(value = SslModeVerifyCa::class, name = "verify-ca"),
    JsonSubTypes.Type(value = SslModeVerifyFull::class, name = "verify-full"),
)
@JsonSchemaTitle("SSL Modes")
@JsonSchemaDescription("SSL connection modes.")
sealed interface SslModeSpecification

@JsonSchemaTitle("disable")
@JsonSchemaDescription("Disables encryption of communication between Airbyte and source database.")
data object SslModeDisable : SslModeSpecification

@JsonSchemaTitle("allow")
@JsonSchemaDescription("Enables encryption only when required by the source database.")
data object SslModeAllow : SslModeSpecification

@JsonSchemaTitle("prefer")
@JsonSchemaDescription(
    "Allows unencrypted connection only if the source database does not support encryption."
)
data object SslModePrefer : SslModeSpecification

@JsonSchemaTitle("require")
@JsonSchemaDescription(
    "Always require encryption. If the source database server does not support encryption, connection will fail."
)
data object SslModeRequire : SslModeSpecification

@JsonSchemaTitle("verify-ca")
@JsonSchemaDescription(
    "Always require encryption and verify that the source database server has a valid SSL certificate."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslModeVerifyCa : SslModeSpecification {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA Certificate")
    @JsonPropertyDescription("CA certificate")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var caCertificate: String

    @JsonProperty("client_certificate")
    @JsonSchemaTitle("Client Certificate")
    @JsonPropertyDescription("Client certificate")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var clientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription("Client key")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var clientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client Key Password")
    @JsonPropertyDescription("Password for the client key, if the key is encrypted.")
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    var clientKeyPassword: String? = null
}

@JsonSchemaTitle("verify-full")
@JsonSchemaDescription(
    "This is the most secure mode. Always require encryption and verify the identity of the source database server."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslModeVerifyFull : SslModeSpecification {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA Certificate")
    @JsonPropertyDescription("CA certificate")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var caCertificate: String

    @JsonProperty("client_certificate")
    @JsonSchemaTitle("Client Certificate")
    @JsonPropertyDescription("Client certificate")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var clientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription("Client key")
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var clientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client Key Password")
    @JsonPropertyDescription("Password for the client key, if the key is encrypted.")
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    var clientKeyPassword: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.ssl_mode")
class MicronautPropertiesFriendlySslModeSpecification {
    var mode: String = "prefer"
    var caCertificate: String? = null

    @JsonValue
    fun asSslMode(): SslModeSpecification =
        when (mode) {
            "disable" -> SslModeDisable
            "allow" -> SslModeAllow
            "prefer" -> SslModePrefer
            "require" -> SslModeRequire
            "verify-ca" -> SslModeVerifyCa().also { it.caCertificate = caCertificate!! }
            "verify-full" -> SslModeVerifyFull().also { it.caCertificate = caCertificate!! }
            else -> throw ConfigErrorException("invalid SSL mode value $mode")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = UserDefinedCursor::class, name = "Standard"),
    JsonSubTypes.Type(value = Xmin::class, name = "Xmin"),
    JsonSubTypes.Type(value = Cdc::class, name = "CDC"),
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface IncrementalConfigurationSpecification

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at)."
)
data object UserDefinedCursor : IncrementalConfigurationSpecification

@JsonSchemaTitle("Detect Changes with Xmin System Column")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts and updates via PostgreSQL's internal Xmin system column. " +
        "Only detects new or changed rows, not deletions. " +
        "No special setup or permissions required. " +
        "Read more at <a href=\"https://docs.airbyte.com/integrations/sources/postgres\">the documentation</a>."
)
data object Xmin : IncrementalConfigurationSpecification

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using PostgreSQL's <a href=" +
        "\"https://docs.airbyte.com/integrations/sources/postgres#cdc\"" +
        "> logical replication feature</a>. This must be enabled on your database."
)
class Cdc : IncrementalConfigurationSpecification {
    @JsonProperty("replication_slot")
    @JsonSchemaTitle("Replication Slot")
    @JsonPropertyDescription(
        "A logical replication slot name created for the CDC sync. " +
            "The slot should be created using the 'pgoutput' plugin."
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true}""")
    lateinit var replicationSlot: String

    @JsonProperty("publication")
    @JsonSchemaTitle("Publication")
    @JsonPropertyDescription(
        "A PostgreSQL publication used for consuming changes. " +
            "All tables must be added to the publication before syncing."
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true}""")
    lateinit var publication: String

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC Position Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value. " +
            "If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. " +
            "If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss."
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(
        json = """{"order":3,"always_show":true, "enum": ["Fail sync","Re-sync data"]}"""
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs."
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":4, "max": 24, "min": 4,"always_show": true}""")
    var initialLoadTimeoutHours: Int? = 8

    @JsonProperty("lsn_commit_behaviour")
    @JsonSchemaTitle("LSN Commit Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines when Airbyte should flush the LSN of processed WAL logs. " +
            "'After each batch' is recommended for most cases. " +
            "'After connector shutdown' can be used for debugging."
    )
    @JsonSchemaDefault("After each batch")
    @JsonSchemaInject(
        json = """{"order":5,"always_show":false, "enum": ["After each batch","After connector shutdown"]}"""
    )
    var lsnCommitBehaviour: String? = "After each batch"
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.replication_method")
class MicronautPropertiesFriendlyIncrementalConfigurationSpecification {
    var method: String = "Standard"
    var replicationSlot: String? = null
    var publication: String? = null

    fun asIncrementalConfiguration(): IncrementalConfigurationSpecification =
        when (method) {
            "Standard" -> UserDefinedCursor
            "Xmin" -> Xmin
            "CDC" -> Cdc().apply {
                replicationSlot = this@MicronautPropertiesFriendlyIncrementalConfigurationSpecification.replicationSlot ?: "airbyte_slot"
                publication = this@MicronautPropertiesFriendlyIncrementalConfigurationSpecification.publication ?: "airbyte_publication"
            }
            else -> throw ConfigErrorException("invalid value $method")
        }
}
