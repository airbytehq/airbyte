/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

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
 * The object which is mapped to the SapHana source configuration JSON.
 *
 * Use [SapHanaSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("SapHana Source Spec")
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
class SapHanaSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("443")
    @JsonPropertyDescription(
        "Port of the database.\n" +
            "SapHana Corporations recommends the following port numbers:\n" +
            "443 - Default listening port for SAP HANA cloud client connections to the listener.",
    )
    var port: Int = 443

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
    fun setCursorMethodValue(value: IncrementalConfigurationSpecification) {
        cursorJson = value
    }

    @JsonGetter("cursor")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":10,"display_type":"radio"}""")
    fun getIncrementalConfigurationSpecificationValue(): IncrementalConfigurationSpecification =
        cursorJson ?: cursor.asIncrementalConfigurationSpecification()

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
    JsonSubTypes.Type(value = EncryptionAlgorithm::class, name = "client_nne"),
    JsonSubTypes.Type(value = SslCertificate::class, name = "encrypted_verify_certificate"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface Encryption

@JsonSchemaTitle("Unencrypted")
@JsonSchemaDescription("Data transfer will not be encrypted.")
data object Unencrypted : Encryption

@JsonSchemaTitle("Native Network Encryption (NNE)")
@JsonSchemaDescription(
    "The native network encryption gives you the ability to encrypt database " +
        "connections, without the configuration overhead of TCP/IP and SSL/TLS " +
        "and without the need to open and listen on different ports.",
)
class EncryptionAlgorithm : Encryption {
    @JsonProperty("encryption_algorithm", required = true)
    @JsonSchemaTitle("Encryption Algorithm")
    @JsonPropertyDescription("This parameter defines what encryption algorithm is used.")
    @JsonSchemaDefault("AES256")
    @JsonSchemaInject(json = """{"enum":["AES256","RC4_56","3DES168"]}""")
    var encryptionAlgorithm: String = "AES256"
}

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
    var encryptionAlgorithm: String? = null
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): Encryption =
        when (encryptionMethod) {
            "unencrypted" -> Unencrypted
            "client_nne" ->
                EncryptionAlgorithm().also { it.encryptionAlgorithm = encryptionAlgorithm!! }
            "encrypted_verify_certificate" ->
                SslCertificate().also { it.sslCertificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $encryptionMethod")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "cursor_method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = UserDefinedCursorConfigurationSpecification::class,
        name = "user_defined",
    ),
    JsonSubTypes.Type(value = CdcCursorConfigurationSpecification::class, name = "cdc"),
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

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using change data capture feature." +
        " This must be enabled on your database.",
)
class CdcCursorConfigurationSpecification : IncrementalConfigurationSpecification {

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC Position Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid " +
            "cursor value in the mined logs. If 'Fail sync' is chosen, a user will have to " +
            "manually reset the connection before being able to continue syncing data. If " +
            "'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could " +
            "lead to higher cloud costs and data loss.",
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(
        json = """{"order":1,"enum":["Fail sync","Re-sync data"],"always_show":true}""",
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC events.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":2,"min":4,"max":24,"always_show":true}""")
    var initialLoadTimeoutHours: Int? = 8
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfigurationSpecification {
    var cursorMethod: String = "user_defined"
    var invalidCdcCursorPositionBehavior: String? = null
    var initialLoadTimeoutHours: Int? = null

    fun asIncrementalConfigurationSpecification(): IncrementalConfigurationSpecification =
        when (cursorMethod) {
            "user_defined" -> UserDefinedCursorConfigurationSpecification
            "cdc" ->
                CdcCursorConfigurationSpecification().also {
                    it.initialLoadTimeoutHours = initialLoadTimeoutHours
                    it.invalidCdcCursorPositionBehavior = invalidCdcCursorPositionBehavior
                }
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
