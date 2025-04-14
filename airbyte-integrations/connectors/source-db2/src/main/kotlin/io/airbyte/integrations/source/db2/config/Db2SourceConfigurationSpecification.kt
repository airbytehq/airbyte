/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.config

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
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Db2 source configuration JSON.
 *
 * Use [Db2SourceConfiguration] instead wherever possible. This object also allows injecting values
 * through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Db2 Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "username",
            "password",
            "database",
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
class Db2SourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("50000")
    @JsonPropertyDescription("Port of the database.")
    var port: Int = 50000

    @JsonProperty("username")
    @JsonSchemaTitle("User")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":3}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":4,"always_show":true,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The database name.")
    @JsonSchemaInject(json = """{"order":5,"always_show":true}""")
    lateinit var database: String

    // TODO: Make optional once this is supported by the CDK:
    //  https://github.com/airbytehq/airbyte/issues/58069
    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription("The list of schemas to sync from.")
    @JsonSchemaInject(json = """{"order":6,"always_show":true,"uniqueItems":true}""")
    lateinit var schemas: List<String>

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
    @ConfigurationBuilder(configurationPrefix = "cursor")
    val cursor = MicronautPropertiesFriendlyCursorConfigurationSpecification()

    @JsonIgnore var cursorJson: IncrementalConfigurationSpecification? = null

    @JsonSetter("cursor")
    fun setIncrementalConfigurationSpecificationValue(
        value: IncrementalConfigurationSpecification
    ) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getIncrementalConfigurationSpecificationValue(): IncrementalConfigurationSpecification =
        // TODO: add CDC
        UserDefinedCursorConfigurationSpecification

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
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "encryption_method")
@JsonSubTypes(
    JsonSubTypes.Type(value = Unencrypted::class, name = "unencrypted"),
    JsonSubTypes.Type(value = SslCertificate::class, name = "encrypted_verify_certificate"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface Encryption

@JsonSchemaTitle("Unencrypted")
@JsonSchemaDescription("Data transfer will not be encrypted.")
data object Unencrypted : Encryption

@JsonSchemaTitle("TLS Encrypted (verify certificate)")
@JsonSchemaDescription("Verify and use the certificate provided by the server.")
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslCertificate : Encryption {
    @JsonProperty("ssl_certificate", required = true)
    @JsonSchemaTitle("SSL PEM File")
    @JsonPropertyDescription(
        "Privacy Enhanced Mail (PEM) files are concatenated certificate " +
            "containers frequently used in certificate installations.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.encryption")
class MicronautPropertiesFriendlyEncryption {
    var encryptionMethod: String = "unencrypted"
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): Encryption =
        when (encryptionMethod) {
            "unencrypted" -> Unencrypted
            "encrypted_verify_certificate" ->
                SslCertificate().also { it.sslCertificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $encryptionMethod")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cursor_method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = UserDefinedCursorConfigurationSpecification::class,
        name = "user_defined"
    ),
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
data object UserDefinedCursorConfigurationSpecification : IncrementalConfigurationSpecification

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfigurationSpecification {}
