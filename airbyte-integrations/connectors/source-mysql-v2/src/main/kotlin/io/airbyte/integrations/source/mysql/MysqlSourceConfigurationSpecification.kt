/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

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
 * The object which is mapped to the Mysql source configuration JSON.
 *
 * Use [MysqlSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Mysql Source Spec")
@JsonPropertyOrder(
    value =
        ["host", "port", "database", "username", "tunnel_method", "ssl_mode", "replication_method"],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MysqlSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("3306")
    @JsonPropertyDescription(
        "Port of the database.",
    )
    var port: Int = 3306

    @JsonProperty("username")
    @JsonSchemaTitle("User")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The database name.")
    @JsonSchemaInject(json = """{"order":6,"always_show":true}""")
    lateinit var database: String

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Params")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3).",
    )
    @JsonSchemaInject(json = """{"order":7}""")
    var jdbcUrlParams: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "ssl_mode")
    var encryption = MicronautPropertiesFriendlyEncryption()

    @JsonIgnore var encryptionJson: Encryption? = null

    @JsonSetter("ssl_mode")
    fun setEncryptionValue(value: Encryption) {
        encryptionJson = value
    }

    @JsonGetter("ssl_mode")
    @JsonSchemaTitle("Encryption")
    @JsonPropertyDescription(
        "The encryption method with is used when communicating with the database.",
    )
    @JsonSchemaInject(json = """{"order":8}""")
    fun getEncryptionValue(): Encryption = encryptionJson ?: encryption.asEncryption()

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
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "replication_method")
    var replicationMethod = MicronautPropertiesFriendlyCursorMethodConfiguration()

    @JsonIgnore var replicationMethodJson: CursorMethodConfiguration? = null

    @JsonSetter("replication_method")
    fun setMethodValue(value: CursorMethodConfiguration) {
        replicationMethodJson = value
    }

    @JsonGetter("replication_method")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getCursorMethodConfigurationValue(): CursorMethodConfiguration =
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
    @JsonSchemaDefault("1")
    @JsonPropertyDescription("Maximum number of concurrent queries to the database.")
    var concurrency: Int? = 1

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":13,"display_type":"check"}""")
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
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(value = EncryptionPreferred::class, name = "preferred"),
    JsonSubTypes.Type(value = EncryptionRequired::class, name = "required"),
    JsonSubTypes.Type(value = SslVerifyCertificate::class, name = "verify_ca"),
    JsonSubTypes.Type(value = SslVerifyIdentity::class, name = "verify_identity"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface Encryption

@JsonSchemaTitle("preferred")
@JsonSchemaDescription(
    "To allow unencrypted communication only when the source doesn't support encryption.",
)
data object EncryptionPreferred : Encryption

@JsonSchemaTitle("required")
@JsonSchemaDescription(
    "To always require encryption. Note: The connection will fail if the source doesn't support encryption.",
)
data object EncryptionRequired : Encryption

@JsonSchemaTitle("verify_ca")
@JsonSchemaDescription(
    "To always require encryption and verify that the source has a valid SSL certificate."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyCertificate : Encryption {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client key password")
    @JsonPropertyDescription(
        "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientPassword: String? = null
}

@JsonSchemaTitle("verify_identity")
@JsonSchemaDescription(
    "To always require encryption and verify that the source has a valid SSL certificate."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyIdentity : Encryption {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client key password")
    @JsonPropertyDescription(
        "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientPassword: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.ssl_mode")
class MicronautPropertiesFriendlyEncryption {
    var mode: String = "preferred"
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): Encryption =
        when (mode) {
            "preferred" -> EncryptionPreferred
            "required" -> EncryptionRequired
            "verify_ca" -> SslVerifyCertificate().also { it.sslCertificate = sslCertificate!! }
            "verify_identity" -> SslVerifyIdentity().also { it.sslCertificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $mode")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = UserDefinedCursor::class, name = "STANDARD"),
    JsonSubTypes.Type(value = CdcCursor::class, name = "CDC")
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface CursorMethodConfiguration

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at).",
)
data object UserDefinedCursor : CursorMethodConfiguration

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using Mysql's <a href=" +
        "\"https://docs.airbyte.com/integrations/sources/mssql/#change-data-capture-cdc\"" +
        "> change data capture feature</a>. This must be enabled on your database.",
)
class CdcCursor : CursorMethodConfiguration {
    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 300 seconds. Valid range: 120 seconds to 1200 seconds. Read about <a href=\" +\n" +
            "        \"\\\"https://docs.airbyte.com/integrations/sources/mysql/#change-data-capture-cdc\\\"\" +\n" +
            "        \"> initial waiting time</a>.",
    )
    @JsonSchemaInject(json = """{"order":1, "max": 1200, "min": 120, "always_show": true}""")
    var initialWaitTimeInSeconds: Int? = 300

    @JsonProperty("server_timezone")
    @JsonSchemaTitle("Configured server timezone for the MySQL source (Advanced)")
    @JsonPropertyDescription(
        "Enter the configured MySQL server timezone. This should only be done if the configured timezone in your MySQL instance does not conform to IANNA standard.",
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true}""")
    var serverTimezone: String? = null

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Configured server timezone for the MySQL source (Advanced)")
    @JsonPropertyDescription(
        "Enter the configured MySQL server timezone. This should only be done if the configured timezone in your MySQL instance does not conform to IANNA standard.",
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(
        json = """{"order":3,"always_show":true, "enum": ["Fail sync","Re-sync data"]}"""
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":4, "max": 24, "min": 4,"always_show": true}""")
    var initialLoadTimeoutHours: Int? = 8
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.replication_method")
class MicronautPropertiesFriendlyCursorMethodConfiguration {
    var method: String = "STANDARD"

    fun asCursorMethodConfiguration(): CursorMethodConfiguration =
        when (method) {
            "STANDARD" -> UserDefinedCursor
            "CDC" -> CdcCursor()
            else -> throw ConfigErrorException("invalid value $method")
        }
}
