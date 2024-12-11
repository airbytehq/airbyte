/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql.config_spec

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
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
 * Use [MysqlSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("MSSQL Source Spec")
@JsonPropertyOrder(
    value = ["host", "port", "database", "schemas", "username", "password"],
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
    @JsonSchemaDefault("3306")
    @JsonPropertyDescription(
        "The port of the database.",
    )
    var port: Int = 3306

    @JsonProperty("database")
    @JsonSchemaTitle("Database")
    @JsonPropertyDescription("The name of the database.")
    @JsonSchemaInject(json = """{"order":2, "examples":["master"]}""")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonPropertyDescription("The list of schemas to sync from. Defaults to user. Case sensitive.")
    // @DefaultSchemaDefault doesn't seem to work for array types...
    @JsonSchemaInject(json = """{"order":3, "default":["dbo"], "minItems":0, "uniqueItems":true}""")
    var schemas: Array<String>? = arrayOf("dbo")

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
    @ConfigurationBuilder(configurationPrefix = "ssl_method")
    var encryption = MicronautPropertiesFriendlyMsSqlServerEncryption()
    @JsonIgnore var encryptionJson: MsSqlServerEncryptionConfigurationSpecification? = null
    @JsonSetter("ssl_method")
    fun setEncryptionValue(value: MsSqlServerEncryptionConfigurationSpecification) {
        encryptionJson = value
    }
    @JsonGetter("ssl_method")
    @JsonSchemaTitle("SSL Method")
    @JsonPropertyDescription(
        "The encryption method which is used when communicating with the database.",
    )
    @JsonSchemaInject(json = """{"order":7}""")
    fun getEncryptionValue(): MsSqlServerEncryptionConfigurationSpecification? =
        encryptionJson ?: encryption.asEncryption()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "method")
    var replicationMethod =
        MsSqlServerMicronautPropertiesFriendlyMsSqlServerReplicationMethodConfiguration()
    @JsonIgnore
    var replicationMethodJson: MsSqlServerReplicationMethodConfigurationSpecification? = null
    @JsonSetter("replication_method")
    fun setReplicationMethodValue(value: MsSqlServerReplicationMethodConfigurationSpecification) {
        replicationMethodJson = value
    }
    @JsonGetter("replication_method")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription(
        "Configures how data is extracted from the database.",
    )
    @JsonSchemaInject(json = """{"order":8, "default":"CDC", "display_type": "radio"}""")
    fun getReplicationMethodValue(): MsSqlServerReplicationMethodConfigurationSpecification? =
        replicationMethodJson ?: replicationMethod.asReplicationMethod()

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
}
