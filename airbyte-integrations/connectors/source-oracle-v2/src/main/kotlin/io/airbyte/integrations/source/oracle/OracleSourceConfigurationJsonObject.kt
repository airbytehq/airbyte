package io.airbyte.integrations.source.oracle

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
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConnectorConfigurationJsonObjectBase
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.commons.exceptions.ConfigErrorException
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Oracle source configuration JSON.
 *
 * Use [OracleSourceConfiguration] instead wherever possible.
 * This object also allows injecting values through Micronaut properties,
 * this is made possible by the classes named `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Oracle Source Spec")
@JsonPropertyOrder(
    value =
    [
        "host",
        "port",
        "connection_data",
        "username",
        "password",
        "schemas",
        "jdbc_url_params",
        "encryption",
    ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class OracleSourceConfigurationJsonObject : ConnectorConfigurationJsonObjectBase() {

    @JsonProperty("host", required = true)
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1}""")
    @JsonPropertyDescription("Hostname of the database.")
    var host: String? = null

    @JsonProperty("port", required = true)
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("1521")
    @JsonPropertyDescription(
        "Port of the database.\n" +
            "Oracle Corporations recommends the following port numbers:\n" +
            "1521 - Default listening port for client connections to the listener. \n" +
            "2484 - Recommended and officially registered listening port for client " +
            "connections to the listener using TCP/IP with SSL.",
    )
    var port: Int? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "connection_data")
    val connectionData = MicronautPropertiesFriendlyConnectionData()

    @JsonIgnore
    var connectionDataJson: ConnectionData? = null

    @JsonSetter("connection_data")
    fun setConnectionDataValue(value: ConnectionData) {
        connectionDataJson = value
    }

    @JsonGetter("connection_data")
    @JsonSchemaInject(json = """{"order":3}""")
    fun getConnectionDataValue(): ConnectionData =
        connectionDataJson ?: connectionData.asConnectionData()


    @JsonProperty("username", required = true)
    @JsonSchemaTitle("User")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4}""")
    var username: String? = null

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret": true}""")
    var password: String? = null

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription("The list of schemas to sync from. Defaults to user. Case sensitive.")
    @JsonSchemaInject(json = """{"order":6,"minItems":1,"uniqueItems":true}""")
    var schemas: List<String> = listOf()

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

    @JsonIgnore
    var encryptionJson: Encryption? = null

    @JsonSetter("encryption")
    fun setEncryptionValue(value: Encryption) {
        encryptionJson = value
    }

    @JsonGetter("encryption")
    @JsonSchemaInject(json = """{"order":8}""")
    fun getEncryptionValue(): Encryption =
        encryptionJson ?: encryption.asEncryption()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject()

    @JsonIgnore
    var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaInject(json = """{"order":9}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnyGetter
    fun getAdditionalProperties(): Map<String, Any> {
        return additionalPropertiesMap
    }

    @JsonAnySetter
    fun setAdditionalProperty(name: String, value: Any) {
        additionalPropertiesMap[name] = value
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "connection_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = ServiceName::class, name = "service_name"),
    JsonSubTypes.Type(value = Sid::class, name = "sid"),
)
@JsonSchemaTitle("Connect by")
@JsonSchemaDescription("Connect data that will be used for DB connection.")
sealed interface ConnectionData

@JsonSchemaTitle("Service name")
@JsonSchemaDescription("Use service name.")
class ServiceName : ConnectionData {

    @JsonProperty("service_name", required = true)
    @JsonSchemaTitle("Service name")
    var serviceName: String? = null
}

@JsonSchemaTitle("System ID (SID)")
@JsonSchemaDescription("Use Oracle System Identifier.")
class Sid : ConnectionData {

    @JsonProperty("sid", required = true)
    @JsonSchemaTitle("System ID (SID)")
    var sid: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.connection_data")
class MicronautPropertiesFriendlyConnectionData {

    var connectionType: String = "service_name"
    var serviceName: String? = null
    var sid: String? = null

    @JsonValue
    fun asConnectionData(): ConnectionData =
        when (connectionType) {
            "service_name" -> ServiceName().also { it.serviceName = serviceName }
            "sid" -> Sid().also { it.sid = sid }
            else -> throw ConfigErrorException("invalid value $connectionType")
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
@JsonSchemaDescription("The native network encryption gives you the ability to encrypt database " +
    "connections, without the configuration overhead of TCP/IP and SSL/TLS and without the need " +
    "to open and listen on different ports.",
)
class EncryptionAlgorithm : Encryption {

    @JsonProperty("encryption_algorithm", required = true)
    @JsonSchemaTitle("Encryption Algorithm")
    @JsonPropertyDescription("This parameter defines what encryption algorithm is used.")
    @JsonSchemaDefault("AES256")
    @JsonSchemaInject(json = """{"enum":["AES256","RC4_56","3DES168"]}""")
    var encryptionAlgorithm: String? = null
}

@JsonSchemaTitle("TLS Encrypted (verify certificate)")
@JsonSchemaDescription("Verify and use the certificate provided by the server.")
class SslCertificate : Encryption {

    @JsonProperty("ssl_certificate", required = true)
    @JsonSchemaTitle("SSL PEM File")
    @JsonPropertyDescription(
        "Privacy Enhanced Mail (PEM) files are concatenated certificate " +
            "containers frequently used in certificate installations.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslCertificate: String? = null
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
                EncryptionAlgorithm().also { it.encryptionAlgorithm = encryptionAlgorithm }
            "encrypted_verify_certificate" ->
                SslCertificate().also { it.sslCertificate = sslCertificate }
            else -> throw ConfigErrorException("invalid value $encryptionMethod")
        }
}
