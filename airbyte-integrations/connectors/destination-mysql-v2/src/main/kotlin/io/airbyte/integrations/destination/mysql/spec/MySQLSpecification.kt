/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.spec

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

sealed class MySQLSpecification : ConfigurationSpecification() {
    abstract val hostname: String
    abstract val port: Int
    abstract val database: String
    abstract val username: String
    abstract val password: String
    abstract val sslMode: MySQLSSLMode
    abstract fun getTunnelMethodValue(): SshTunnelMethodConfiguration?
}

@Singleton
@Requires(notEnv = [AIRBYTE_CLOUD_ENV])
class MySQLSpecificationOss : MySQLSpecification() {
    @get:JsonSchemaTitle("Hostname")
    @get:JsonPropertyDescription("Hostname of the MySQL database server.")
    @get:JsonProperty("hostname")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    override val hostname: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("Port of the MySQL database server. Default is 3306.")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": 3306}""")
    override val port: Int = 3306

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database to sync data to.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 2}""")
    override val database: String = ""

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to use to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 3}""")
    override val username: String = ""

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    override val password: String = ""

    @get:JsonSchemaTitle("SSL Mode")
    @get:JsonPropertyDescription("SSL connection mode. Use 'preferred' for encrypted connections when available.")
    @get:JsonProperty("ssl_mode")
    @get:JsonSchemaInject(json = """{"order": 5, "default": "preferred"}""")
    override val sslMode: MySQLSSLMode = MySQLSSLMode.PREFERRED

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore
    var tunnelConfig: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration?) {
        tunnelConfig = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, " +
            "and if so, which kind of authentication to use."
    )
    @JsonSchemaInject(json = """{"order": 6}""")
    override fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelConfig ?: tunnelMethod.asSshTunnelMethod()
}

@Singleton
@Requires(env = [AIRBYTE_CLOUD_ENV])
class MySQLSpecificationCloud : MySQLSpecification() {
    @get:JsonSchemaTitle("Hostname")
    @get:JsonPropertyDescription("Hostname of the MySQL database server.")
    @get:JsonProperty("hostname")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    override val hostname: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("Port of the MySQL database server. Default is 3306.")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": 3306}""")
    override val port: Int = 3306

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the database to sync data to.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 2}""")
    override val database: String = ""

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to use to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 3}""")
    override val username: String = ""

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    override val password: String = ""

    @get:JsonSchemaTitle("SSL Mode")
    @get:JsonPropertyDescription("SSL connection mode. Use 'required' for encrypted connections.")
    @get:JsonProperty("ssl_mode")
    @get:JsonSchemaInject(json = """{"order": 5, "default": "required", "airbyte_hidden": true}""")
    override val sslMode: MySQLSSLMode = MySQLSSLMode.REQUIRED

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore
    var tunnelConfig: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration?) {
        tunnelConfig = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, " +
            "and if so, which kind of authentication to use."
    )
    @JsonSchemaInject(json = """{"order": 6}""")
    override fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelConfig ?: tunnelMethod.asSshTunnelMethod()
}

enum class MySQLSSLMode(@get:JsonValue val value: String) {
    DISABLED("disabled"),
    PREFERRED("preferred"),
    REQUIRED("required"),
    VERIFY_CA("verify_ca"),
    VERIFY_IDENTITY("verify_identity")
}
