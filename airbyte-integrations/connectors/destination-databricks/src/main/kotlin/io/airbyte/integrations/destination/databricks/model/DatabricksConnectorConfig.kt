package io.airbyte.integrations.destination.databricks.model

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonTypeName
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.module.kotlin.kotlinModule
import io.airbyte.commons.jackson.MoreMappers

data class DatabricksConnectorConfig(
    @JsonProperty("accept_terms") val termsAccepted: Boolean,
    @JsonProperty("hostname") val hostName: String,
    @JsonProperty("port") val port: Int = 443,
    @JsonProperty("http_path") val httpPath: String,
    val database: String,
    val schema: String = "default",
    val enableSchemaEvolution: Boolean = false,
    @JsonProperty("api_authentication") val apiAuthentication: ApiAuthentication,
    @JsonProperty("jdbc_authentication") val jdbcAuthentication: JdbcAuthentication
) {
    companion object {
        fun deserialize(jsonNode: JsonNode): DatabricksConnectorConfig {
            val objectMapper = MoreMappers.initMapper()
            objectMapper.registerModule(kotlinModule())
            return objectMapper.convertValue(jsonNode, DatabricksConnectorConfig::class.java)
        }
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "auth_type")
sealed interface ApiAuthentication {
    @JsonTypeName("PERSONAL_ACCESS_TOKEN")
    data class PersonalAccessToken(val token: String): ApiAuthentication

    @JsonTypeName("OAUTH_TOKEN")
    data class OAuthToken(val token: String): ApiAuthentication

}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "auth_type")
sealed interface JdbcAuthentication {

    @JsonTypeName("BASIC")
    data class BasicAuthentication(val username: String, val password : String): JdbcAuthentication

    @JsonTypeName("OAUTH")
    data class OIDCAuthentication(val oauthToken: String): JdbcAuthentication
}
