/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

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
 * The object which is mapped to the MS SQL Server source configuration JSON.
 *
 * Use [MsSqlServerSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("MSSQL Source Spec")
@JsonPropertyOrder(
    value = ["host", "port", "database", "username", "replication_method"],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MsSqlServerSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":0}""")
    @JsonPropertyDescription("The hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":1,"minimum": 0,"maximum": 65536, "examples":["1433"]}""")
    @JsonSchemaDefault("1433")
    @JsonPropertyDescription(
        "The port of the database.",
    )
    var port: Int = 1433

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The name of the database.")
    @JsonSchemaInject(json = """{"order":2, "examples":["master"]}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonPropertyDescription(
        "The list of schemas to sync from. If not specified, all schemas will be discovered. Case sensitive."
    )
    @JsonSchemaInject(json = """{"order":3, "minItems":0, "uniqueItems":true}""")
    var schemas: Array<String>? = null

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret":true}""")
    lateinit var password: String

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3).",
    )
    @JsonSchemaInject(json = """{"order":6}""")
    var jdbcUrlParams: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "ssl_mode")
    var encryption = MicronautPropertiesFriendlyEncryptionSpecification()

    @JsonIgnore var encryptionJson: EncryptionSpecification? = null

    @JsonSetter("ssl_mode")
    fun setEncryptionValue(value: EncryptionSpecification) {
        encryptionJson = value
    }

    @JsonGetter("ssl_mode")
    @JsonSchemaTitle("Encryption")
    @JsonPropertyDescription(
        "The encryption method which is used when communicating with the database.",
    )
    @JsonSchemaInject(json = """{"order":8,"default":"required"}""")
    fun getEncryptionValue(): EncryptionSpecification? = encryptionJson ?: encryption.asEncryption()

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
            "and if so, which kind of authentication to use.",
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
        replicationMethodJson ?: replicationMethod.asCursorMethodConfiguration()

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":11}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonSchemaInject(json = """{"order":12}""")
    @JsonPropertyDescription("Maximum number of concurrent queries to the database.")
    var concurrency: Int? = null

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":13}""")
    @JsonSchemaDefault("true")
    @JsonPropertyDescription(
        "When this feature is enabled, during schema discovery the connector " +
            "will query each table or view individually to check access privileges " +
            "and inaccessible tables, views, or columns therein will be removed. " +
            "In large schemas, this might cause schema discovery to take too long, " +
            "in which case it might be advisable to disable this feature.",
    )
    var checkPrivileges: Boolean? = true

    @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnyGetter fun getAdditionalProperties(): Map<String, Any> = additionalPropertiesMap

    @JsonAnySetter
    fun setAdditionalProperty(
        name: String,
        value: Any,
    ) {
        additionalPropertiesMap[name] = value
    }

    companion object {
        const val DEFAULT_HEARTBEAT_INTERVAL_MS = 15000L
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = MsSqlServerEncryptionDisabledConfigurationSpecification::class,
        name = "unencrypted"
    ),
    JsonSubTypes.Type(
        value =
            MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification::class,
        name = "encrypted_trust_server_certificate"
    ),
    JsonSubTypes.Type(value = SslVerifyCertificate::class, name = "encrypted_verify_certificate"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface EncryptionSpecification

@JsonSchemaTitle("Unencrypted")
@JsonSchemaDescription(
    "Data transfer will not be encrypted.",
)
data object MsSqlServerEncryptionDisabledConfigurationSpecification : EncryptionSpecification

@JsonSchemaTitle("Encrypted (trust server certificate)")
@JsonSchemaDescription(
    "Use the certificate provided by the server without verification. (For testing purposes only!)"
)
data object MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification :
    EncryptionSpecification

@JsonSchemaTitle("Encrypted (verify certificate)")
@JsonSchemaDescription("Verify and use the certificate provided by the server.")
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyCertificate : EncryptionSpecification {
    @JsonProperty("hostNameInCertificate")
    @JsonSchemaTitle("Host Name In Certificate")
    @JsonPropertyDescription(
        "Specifies the host name of the server. The value of this property must match the subject property of the certificate.",
    )
    @JsonSchemaInject(json = """{"order":0}""")
    var hostNameInCertificate: String? = null

    @JsonProperty("certificate", required = false)
    @JsonSchemaTitle("Certificate")
    @JsonPropertyDescription(
        "certificate of the server, or of the CA that signed the server certificate",
    )
    @JsonSchemaInject(json = """{"order":1,"airbyte_secret":true,"multiline":true}""")
    var certificate: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.ssl_mode")
class MicronautPropertiesFriendlyEncryptionSpecification {
    var mode: String = "unencrypted"
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): EncryptionSpecification =
        when (mode) {
            "unencrypted" -> MsSqlServerEncryptionDisabledConfigurationSpecification
            "Encrypted (trust server certificate)" ->
                MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification
            "Encrypted (verify certificate)" ->
                SslVerifyCertificate().also { it.certificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $mode")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = UserDefinedCursor::class, name = "STANDARD"),
    JsonSubTypes.Type(value = Cdc::class, name = "CDC")
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface IncrementalConfigurationSpecification

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at).",
)
class UserDefinedCursor : IncrementalConfigurationSpecification {
    @JsonProperty("exclude_todays_data")
    @JsonSchemaTitle("Exclude Today's Data")
    @JsonPropertyDescription(
        "When enabled incremental syncs using a cursor of a temporal type (date or datetime) will include cursor values only up until the previous midnight UTC"
    )
    @JsonSchemaDefault("false")
    @JsonSchemaInject(json = """{"order":1,"always_show":true}""")
    var excludeTodaysData: Boolean? = false
}

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using MSSQL's <a href=" +
        "\"https://docs.airbyte.com/integrations/sources/mssql/#change-data-capture-cdc\"" +
        "> change data capture feature</a>. This must be enabled on your database.",
)
class Cdc : IncrementalConfigurationSpecification {
    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonPropertyDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 3600 seconds. Read about <a href=\"https://docs.airbyte.com/integrations/sources/mssql#setting-up-cdc-for-mssql\">initial waiting time</a>"
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true}""")
    var initialWaitingSeconds: Int? = null

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC Position Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value in the mined logs. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.",
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(
        json = """{"order":2,"always_show":true, "enum": ["Fail sync","Re-sync data"]}"""
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":3, "max": 24, "min": 4,"always_show": true}""")
    var initialLoadTimeoutHours: Int? = 8

    @JsonProperty("poll_interval_ms")
    @JsonSchemaTitle("Poll Interval in Milliseconds (Advanced)")
    @JsonPropertyDescription(
        "How often (in milliseconds) Debezium should poll for new data. Must be smaller than heartbeat interval (15000ms). Lower values provide more responsive data capture but may increase database load.",
    )
    @JsonSchemaDefault("500")
    @JsonSchemaInject(json = """{"order":4, "max": 14999, "min": 100,"always_show": true}""")
    var pollIntervalMs: Int? = 500
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.replication_method")
class MicronautPropertiesFriendlyIncrementalConfigurationSpecification {
    var method: String = "STANDARD"

    fun asCursorMethodConfiguration(): IncrementalConfigurationSpecification =
        when (method) {
            "STANDARD" -> UserDefinedCursor()
            "CDC" -> Cdc()
            else -> throw ConfigErrorException("invalid value $method")
        }
}
