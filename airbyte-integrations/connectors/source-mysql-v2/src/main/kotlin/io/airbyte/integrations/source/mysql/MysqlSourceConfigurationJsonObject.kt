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
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaArrayWithUniqueItems
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject
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
        [
            "host",
            "port",
            "username",
            "password",
            "schemas",
            "jdbc_url_params",
            "encryption",
            "tunnel_method",
            "cursor",
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MysqlSourceConfigurationJsonObject : ConfigurationJsonObjectBase() {
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

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription("The list of schemas to sync from. Defaults to user. Case sensitive.")
    @JsonSchemaInject(json = """{"order":6,"always_show":true,"uniqueItems":true}""")
    var schemas: List<String>? = null

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
    @ConfigurationBuilder(configurationPrefix = "encryption")
    val encryption = MicronautPropertiesFriendlyEncryption()

    @JsonIgnore var encryptionJson: Encryption? = null

    @JsonSetter("encryption")
    fun setEncryptionValue(value: Encryption) {
        encryptionJson = value
    }

    @JsonGetter("encryption")
    @JsonSchemaTitle("Encryption")
    @JsonPropertyDescription(
        "The encryption method with is used when communicating with the database.",
    )
    @JsonSchemaInject(json = """{"order":8}""")
    fun getEncryptionValue(): Encryption = encryptionJson ?: encryption.asEncryption()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject()

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
    @ConfigurationBuilder(configurationPrefix = "cursor")
    val cursor = MicronautPropertiesFriendlyCursorConfiguration()

    @JsonIgnore var cursorJson: CursorConfiguration? = null

    @JsonSetter("cursor")
    fun setCursorMethodValue(value: CursorConfiguration) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getCursorConfigurationValue(): CursorConfiguration =
        cursorJson ?: cursor.asCursorConfiguration()

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

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "encryption_method")
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
    @JsonProperty("ssl_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("ssl_client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("ssl_client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("ssl_client_key_password")
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
    @JsonProperty("ssl_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("ssl_client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("ssl_client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("ssl_client_key_password")
    @JsonSchemaTitle("Client key password")
    @JsonPropertyDescription(
        "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientPassword: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.encryption")
class MicronautPropertiesFriendlyEncryption {
    var encryptionMethod: String = "preferred"
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): Encryption =
        when (encryptionMethod) {
            "preferred" -> EncryptionPreferred
            "required" -> EncryptionRequired
            "verify_ca" -> SslVerifyCertificate().also { it.sslCertificate = sslCertificate!! }
            "verify_identity" -> SslVerifyIdentity().also { it.sslCertificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $encryptionMethod")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cursor_method")
@JsonSubTypes(
    JsonSubTypes.Type(value = UserDefinedCursor::class, name = "user_defined"),
    JsonSubTypes.Type(value = CdcCursor::class, name = "cdc")
    // TODO: port over additional Cdc options
    )
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface CursorConfiguration

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at).",
)
data object UserDefinedCursor : CursorConfiguration

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using Mysql's <a href=" +
        "\"https://docs.airbyte.com/integrations/sources/mssql/#change-data-capture-cdc\"" +
        "> change data capture feature</a>. This must be enabled on your database.",
)
data object CdcCursor : CursorConfiguration

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfiguration {
    var cursorMethod: String = "user_defined"

    fun asCursorConfiguration(): CursorConfiguration =
        when (cursorMethod) {
            "user_defined" -> UserDefinedCursor
            "cdc" -> CdcCursor
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
