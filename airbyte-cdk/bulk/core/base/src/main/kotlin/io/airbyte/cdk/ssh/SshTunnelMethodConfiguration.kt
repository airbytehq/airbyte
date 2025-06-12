/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.micronaut.context.annotation.ConfigurationProperties

/** Union type for SSH tunnel method configuration in connector configurations. */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "tunnel_method")
@JsonSubTypes(
    JsonSubTypes.Type(value = SshNoTunnelMethod::class, name = "NO_TUNNEL"),
    JsonSubTypes.Type(value = SshKeyAuthTunnelMethod::class, name = "SSH_KEY_AUTH"),
    JsonSubTypes.Type(value = SshPasswordAuthTunnelMethod::class, name = "SSH_PASSWORD_AUTH"),
)
@JsonSchemaTitle("SSH Tunnel Method")
@JsonSchemaDescription(
    "Whether to initiate an SSH tunnel before connecting to the database, " +
        "and if so, which kind of authentication to use.",
)
sealed interface SshTunnelMethodConfiguration

@JsonSchemaTitle("No Tunnel")
@JsonSchemaDescription("No ssh tunnel needed to connect to database")
data object SshNoTunnelMethod : SshTunnelMethodConfiguration

@JsonSchemaTitle("SSH Key Authentication")
@JsonSchemaDescription("Connect through a jump server tunnel host using username and ssh key")
data class SshKeyAuthTunnelMethod(
    @get:JsonProperty("tunnel_host", required = true)
    @param:JsonProperty("tunnel_host", required = true)
    @JsonSchemaTitle("SSH Tunnel Jump Server Host")
    @JsonPropertyDescription("Hostname of the jump server host that allows inbound ssh tunnel.")
    @JsonSchemaInject(json = """{"order":1}""")
    val host: String,
    @get:JsonProperty("tunnel_port", required = true)
    @param:JsonProperty("tunnel_port", required = true)
    @JsonSchemaTitle("SSH Connection Port")
    @JsonPropertyDescription("Port on the proxy/jump server that accepts inbound ssh connections.")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("22")
    val port: Int,
    @get:JsonProperty("tunnel_user", required = true)
    @param:JsonProperty("tunnel_user", required = true)
    @JsonSchemaTitle("SSH Login Username")
    @JsonPropertyDescription("OS-level username for logging into the jump server host")
    @JsonSchemaInject(json = """{"order":3}""")
    val user: String,
    @get:JsonProperty("ssh_key", required = true)
    @param:JsonProperty("ssh_key", required = true)
    @JsonSchemaTitle("SSH Private Key")
    @JsonPropertyDescription(
        "OS-level user account ssh key credentials in RSA PEM format " +
            "( created with ssh-keygen -t rsa -m PEM -f myuser_rsa )",
    )
    @JsonSchemaInject(json = """{"order":4,"multiline":true,"airbyte_secret": true}""")
    val key: String,
) : SshTunnelMethodConfiguration

@JsonSchemaTitle("Password Authentication")
@JsonSchemaDescription(
    "Connect through a jump server tunnel host using username and password authentication",
)
data class SshPasswordAuthTunnelMethod(
    @get:JsonProperty("tunnel_host", required = true)
    @param:JsonProperty("tunnel_host", required = true)
    @JsonSchemaTitle("SSH Tunnel Jump Server Host")
    @JsonPropertyDescription("Hostname of the jump server host that allows inbound ssh tunnel.")
    @JsonSchemaInject(json = """{"order":1}""")
    val host: String,
    @get:JsonProperty("tunnel_port", required = true)
    @param:JsonProperty("tunnel_port", required = true)
    @JsonSchemaTitle("SSH Connection Port")
    @JsonPropertyDescription("Port on the proxy/jump server that accepts inbound ssh connections.")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536}""")
    @JsonSchemaDefault("22")
    val port: Int,
    @get:JsonProperty("tunnel_user", required = true)
    @param:JsonProperty("tunnel_user", required = true)
    @JsonSchemaTitle("SSH Login Username")
    @JsonPropertyDescription("OS-level username for logging into the jump server host")
    @JsonSchemaInject(json = """{"order":3}""")
    val user: String,
    @get:JsonProperty("tunnel_user_password", required = true)
    @param:JsonProperty("tunnel_user_password", required = true)
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("OS-level password for logging into the jump server host")
    @JsonSchemaInject(json = """{"order":4,"airbyte_secret": true}""")
    val password: String,
) : SshTunnelMethodConfiguration

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.tunnel_method")
class MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification {
    var tunnelMethod: String = "NO_TUNNEL"
    var tunnelHost: String? = null
    var tunnelPort: Int = 22
    var tunnelUser: String? = null
    var sshKey: String? = null
    var tunnelUserPassword: String? = null

    @JsonValue
    fun asSshTunnelMethod(): SshTunnelMethodConfiguration =
        when (tunnelMethod) {
            "NO_TUNNEL" -> SshNoTunnelMethod
            "SSH_KEY_AUTH" ->
                SshKeyAuthTunnelMethod(tunnelHost!!, tunnelPort, tunnelUser!!, sshKey!!)
            "SSH_PASSWORD_AUTH" ->
                SshPasswordAuthTunnelMethod(
                    tunnelHost!!,
                    tunnelPort,
                    tunnelUser!!,
                    tunnelUserPassword!!,
                )
            else -> throw ConfigErrorException("invalid value $tunnelMethod")
        }
}
