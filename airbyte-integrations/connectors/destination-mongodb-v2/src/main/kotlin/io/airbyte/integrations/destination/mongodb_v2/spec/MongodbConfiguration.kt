/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class MongodbConfiguration(
    @JsonProperty("connection_string")
    @JsonPropertyDescription("MongoDB connection string (e.g., mongodb://localhost:27017)")
    val connectionString: String,
    @JsonProperty("database")
    @JsonPropertyDescription("Name of the database to write to")
    val database: String,
    @JsonProperty("auth_type")
    @JsonPropertyDescription("Authentication type")
    val authType: AuthType = AuthType.LOGIN_PASSWORD,
    @JsonProperty("username")
    @JsonPropertyDescription("Username for authentication")
    val username: String? = null,
    @JsonProperty("password")
    @JsonPropertyDescription("Password for authentication")
    val password: String? = null,
    @JsonProperty("batch_size")
    @JsonPropertyDescription("Number of documents to buffer before flushing (default: 1000)")
    val batchSize: Int = 1000,
    @JsonProperty("tunnel_method")
    @JsonPropertyDescription("SSH tunnel configuration")
    val tunnelMethod: TunnelMethod? = null,
) : DestinationConfiguration() {

    enum class AuthType(@get:JsonValue val value: String) {
        @JsonProperty("login_password") LOGIN_PASSWORD("login/password"),
        @JsonProperty("none") NONE("none")
    }

    data class TunnelMethod(
        @JsonProperty("tunnel_method") val tunnelMethod: String,
        @JsonProperty("tunnel_host") val tunnelHost: String? = null,
        @JsonProperty("tunnel_port") val tunnelPort: Int? = null,
        @JsonProperty("tunnel_user") val tunnelUser: String? = null,
        @JsonProperty("ssh_key") val sshKey: String? = null,
    )
}

@Singleton
class MongodbConfigurationFactory(
    private val specFactory: MongodbConfigurationSpecificationSupplier,
) : DestinationConfigurationFactory<MongodbSpecification, MongodbConfiguration> {

    override fun makeWithoutExceptionHandling(spec: MongodbSpecification): MongodbConfiguration {
        return MongodbConfiguration(
            connectionString = spec.connectionString,
            database = spec.database,
            authType = spec.authType ?: MongodbConfiguration.AuthType.NONE,
            username = spec.username,
            password = spec.password,
            batchSize = spec.batchSize ?: 1000,
            tunnelMethod = spec.tunnelMethod,
        )
    }

    override fun make(spec: MongodbSpecification): MongodbConfiguration {
        val config = makeWithoutExceptionHandling(spec)

        // Validate configuration
        if (config.authType == MongodbConfiguration.AuthType.LOGIN_PASSWORD) {
            require(!config.username.isNullOrBlank()) {
                "Username is required when using login/password authentication"
            }
            require(!config.password.isNullOrBlank()) {
                "Password is required when using login/password authentication"
            }
        }

        require(config.batchSize > 0) { "Batch size must be greater than 0" }

        return config
    }
}

@Factory
class MongodbConfigurationSpecificationSupplier {
    @Singleton
    fun get(): MongodbSpecification {
        // This would typically load from a JSON spec file
        // For now, return a default specification
        return MongodbSpecification(
            connectionString = "",
            database = "",
        )
    }
}
