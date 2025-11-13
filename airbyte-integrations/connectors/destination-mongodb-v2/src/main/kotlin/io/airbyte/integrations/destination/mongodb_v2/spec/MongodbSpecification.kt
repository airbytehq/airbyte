/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import io.airbyte.cdk.command.ConfigurationSpecification

data class MongodbSpecification(
    @JsonProperty("connection_string")
    @JsonPropertyDescription("MongoDB connection string")
    val connectionString: String,

    @JsonProperty("database")
    @JsonPropertyDescription("Database name")
    val database: String,

    @JsonProperty("auth_type")
    val authType: MongodbConfiguration.AuthType? = null,

    @JsonProperty("username")
    val username: String? = null,

    @JsonProperty("password")
    val password: String? = null,

    @JsonProperty("batch_size")
    val batchSize: Int? = null,

    @JsonProperty("tunnel_method")
    val tunnelMethod: MongodbConfiguration.TunnelMethod? = null,
) : ConfigurationSpecification()
