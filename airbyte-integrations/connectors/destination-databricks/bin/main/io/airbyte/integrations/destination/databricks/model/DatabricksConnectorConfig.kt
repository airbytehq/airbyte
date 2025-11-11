/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.model

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonTypeName
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.module.kotlin.kotlinModule
import io.airbyte.commons.jackson.MoreMappers

data class DatabricksConnectorConfig(
    @JsonProperty("accept_terms") val termsAccepted: Boolean,
    val hostname: String,
    val port: Int = 443,
    @JsonProperty("http_path") val httpPath: String,
    val database: String,
    val schema: String = "default",
    @JsonProperty("raw_schema_override") val rawSchemaOverride: String = "airbyte_internal",
    @JsonProperty("authentication") val authentication: Authentication,
    @JsonProperty("purge_staging_data") val purgeStagingData: Boolean = true,
) {
    companion object {
        fun deserialize(jsonNode: JsonNode): DatabricksConnectorConfig {
            val objectMapper = MoreMappers.initMapper()
            objectMapper.registerModule(kotlinModule())
            return objectMapper.convertValue(jsonNode, DatabricksConnectorConfig::class.java)
        }
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "auth_type") sealed interface Authentication

@JsonTypeName("BASIC")
data class BasicAuthentication(
    @JsonProperty("personal_access_token") val personalAccessToken: String,
) : Authentication

@JsonTypeName("OAUTH")
data class OAuth2Authentication(
    @JsonProperty("client_id") val clientId: String,
    val secret: String
) : Authentication
