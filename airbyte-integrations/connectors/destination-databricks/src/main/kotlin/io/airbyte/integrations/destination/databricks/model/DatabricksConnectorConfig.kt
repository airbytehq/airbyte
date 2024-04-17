package io.airbyte.integrations.destination.databricks.model

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonTypeName

data class DatabricksConnectorConfig(
    @JsonProperty("accept_terms") val termsAccepted: Boolean,
    @JsonProperty("hostname") val hostName: String,
    @JsonProperty("http_path") val httpPath: String,
    @JsonProperty("api_authentication") val apiAuthentication: ApiAuthentication,
    @JsonProperty("jdbc_authentication") val jdbcAuthentication: JdbcAuthentication
)

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
