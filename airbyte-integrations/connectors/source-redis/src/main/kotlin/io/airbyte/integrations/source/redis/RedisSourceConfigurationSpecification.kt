/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import jakarta.inject.Singleton

@JsonSchemaTitle("Redis Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "username",
            "password",
            "database",
            "ssl_mode",
            "key_pattern",
            "tunnel_method",
            "scan_batch_size",
            "checkpoint_target_interval_seconds",
            "max_db_connections",
        ],
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class RedisSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host", required = true)
    @JsonSchemaTitle("Host")
    @JsonPropertyDescription("The hostname or IP address of the Redis server.")
    @JsonSchemaInject(json = """{"order":0,"examples":["redis.example.com"]}""")
    lateinit var host: String

    @JsonProperty("port", required = true)
    @JsonSchemaTitle("Port")
    @JsonPropertyDescription("The port on which Redis is listening.")
    @JsonSchemaInject(json = """{"order":1,"default":6379,"minimum":1,"maximum":65535}""")
    var port: Int = DEFAULT_PORT

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("Optional Redis ACL username. Leave empty for the default user.")
    @JsonSchemaInject(json = """{"order":2}""")
    var username: String? = null

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("Optional Redis password.")
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    var password: String? = null

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The Redis logical database index.")
    @JsonSchemaInject(json = """{"order":4,"default":0,"minimum":0}""")
    var database: Int? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "ssl_mode")
    var sslMode = MicronautPropertiesFriendlyRedisSslModeSpecification()

    @JsonIgnore var sslModeJson: RedisSslModeConfiguration? = null

    @JsonGetter("ssl_mode")
    @JsonSchemaTitle("SSL Mode")
    @JsonPropertyDescription("The TLS mode used to connect to Redis.")
    @JsonSchemaInject(json = """{"order":5}""")
    fun getSslModeValue(): RedisSslModeConfiguration? = sslModeJson ?: sslMode.asSslMode()

    @JsonSetter("ssl_mode")
    fun setSslModeValue(value: RedisSslModeConfiguration) {
        sslModeJson = value
    }

    @JsonProperty("key_pattern")
    @JsonSchemaTitle("Key Pattern")
    @JsonPropertyDescription(
        "The Redis glob pattern to include. Discovery is static and does not scan keys.",
    )
    @JsonSchemaInject(json = """{"order":6,"default":"*","examples":["*","app:*"]}""")
    var keyPattern: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription("Whether to connect to Redis through an SSH tunnel.")
    @JsonSchemaInject(json = """{"order":7}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonProperty("scan_batch_size")
    @JsonSchemaTitle("SCAN Batch Size")
    @JsonPropertyDescription("The number of keys Redis should return per SCAN request.")
    @JsonSchemaInject(json = """{"order":8,"default":1000,"minimum":1}""")
    var scanBatchSize: Int? = null

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Interval (Seconds)")
    @JsonPropertyDescription("The target interval between checkpoints.")
    @JsonSchemaInject(json = """{"order":9,"default":300,"minimum":1}""")
    var checkpointTargetIntervalSeconds: Int? = null

    @JsonProperty("max_db_connections")
    @JsonSchemaTitle("Max Concurrent Queries to Database")
    @JsonPropertyDescription("The maximum number of concurrent Redis connections.")
    @JsonSchemaInject(json = """{"order":10,"minimum":1}""")
    var maxDbConnections: Int? = null

    companion object {
        const val DEFAULT_PORT = 6379
        const val DEFAULT_DATABASE = 0
        const val DEFAULT_KEY_PATTERN = "*"
        const val DEFAULT_SCAN_BATCH_SIZE = 1000
        const val DEFAULT_CHECKPOINT_TARGET_INTERVAL_SECONDS = 300
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(value = RedisSslDisabled::class, name = "disable"),
    JsonSubTypes.Type(value = RedisSslRequired::class, name = "require"),
    JsonSubTypes.Type(value = RedisSslVerifyCa::class, name = "verify-ca"),
    JsonSubTypes.Type(value = RedisSslVerifyFull::class, name = "verify-full"),
)
@JsonSchemaTitle("SSL Mode")
@JsonSchemaDescription("The TLS mode used when communicating with Redis.")
sealed interface RedisSslModeConfiguration

@JsonSchemaTitle("Disable")
@JsonSchemaDescription("Connect without TLS.")
data object RedisSslDisabled : RedisSslModeConfiguration

@JsonSchemaTitle("Require")
@JsonSchemaDescription("Use TLS without validating the server certificate.")
data object RedisSslRequired : RedisSslModeConfiguration

@JsonSchemaTitle("Verify CA")
@JsonSchemaDescription("Use TLS and validate the server certificate against a trusted CA.")
class RedisSslVerifyCa : RedisSslModeConfiguration {
    @JsonProperty("ca_certificate")
    @JsonSchemaTitle("CA Certificate")
    @JsonSchemaInject(json = """{"order":0,"multiline":true}""")
    var caCertificate: String? = null

    @JsonProperty("client_certificate")
    @JsonSchemaTitle("Client Certificate")
    @JsonSchemaInject(json = """{"order":1,"multiline":true}""")
    var clientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonSchemaInject(json = """{"order":2,"multiline":true,"airbyte_secret":true}""")
    var clientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client Key Password")
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    var clientKeyPassword: String? = null
}

@JsonSchemaTitle("Verify Full")
@JsonSchemaDescription("Use TLS and validate the server certificate and hostname.")
class RedisSslVerifyFull : RedisSslModeConfiguration {
    @JsonProperty("ca_certificate")
    @JsonSchemaTitle("CA Certificate")
    @JsonSchemaInject(json = """{"order":0,"multiline":true}""")
    var caCertificate: String? = null

    @JsonProperty("client_certificate")
    @JsonSchemaTitle("Client Certificate")
    @JsonSchemaInject(json = """{"order":1,"multiline":true}""")
    var clientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonSchemaInject(json = """{"order":2,"multiline":true,"airbyte_secret":true}""")
    var clientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client Key Password")
    @JsonSchemaInject(json = """{"order":3,"airbyte_secret":true}""")
    var clientKeyPassword: String? = null
}

class MicronautPropertiesFriendlyRedisSslModeSpecification {
    var mode: String = "disable"
    var caCertificate: String? = null
    var clientCertificate: String? = null
    var clientKey: String? = null
    var clientKeyPassword: String? = null

    @JsonValue
    fun asSslMode(): RedisSslModeConfiguration =
        when (mode) {
            "disable" -> RedisSslDisabled
            "require" -> RedisSslRequired
            "verify-ca" ->
                RedisSslVerifyCa().also {
                    it.caCertificate = caCertificate
                    it.clientCertificate = clientCertificate
                    it.clientKey = clientKey
                    it.clientKeyPassword = clientKeyPassword
                }
            "verify-full" ->
                RedisSslVerifyFull().also {
                    it.caCertificate = caCertificate
                    it.clientCertificate = clientCertificate
                    it.clientKey = clientKey
                    it.clientKeyPassword = clientKeyPassword
                }
            else -> throw IllegalArgumentException("Invalid ssl_mode '$mode'.")
        }
}
