/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.micronaut.context.annotation.ConfigurationProperties

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "authentication_method")
@JsonSubTypes(
    JsonSubTypes.Type(value = PasswordAuthentication::class, name = "password_authentication"),
    JsonSubTypes.Type(value = TokenBasedAuthentication::class, name = "token_based_authentication"),
)
@JsonSchemaTitle("Authentication Method")
@JsonSchemaDescription(
    "Configure how to authenticate to Netsuite. " +
        "Options include username/password or token-based authentication."
)
sealed interface AuthenticationMethodConfiguration

@JsonSchemaTitle("Password Authentication")
@JsonSchemaDescription("Authenticate using a password.")
data class PasswordAuthentication(
    @get:JsonProperty("password", required = true)
    @param:JsonProperty("password", required = true)
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(json = """{"order":1,"airbyte_secret":true}""")
    var password: String? = null,
) : AuthenticationMethodConfiguration

@JsonSchemaTitle("Token Based Authentication")
@JsonSchemaDescription(
    "Authenticate using a token-based authentication method. " +
        "This requires a consumer key and secret, as well as a token ID and secret."
)
data class TokenBasedAuthentication(
    @get:JsonProperty("client_id", required = true)
    @param:JsonProperty("client_id", required = true)
    @JsonSchemaTitle("Consumer Key")
    @JsonPropertyDescription(
        "The consumer key used for token-based authentication. " +
            "This is generated in NetSuite when creating an integration record."
    )
    @JsonSchemaInject(json = """{"order":1}""")
    val clientId: String,
    @get:JsonProperty("client_secret", required = true)
    @param:JsonProperty("client_secret", required = true)
    @JsonSchemaTitle("Consumer Secret")
    @JsonPropertyDescription(
        "The consumer secret used for token-based authentication. " +
            "This is generated in NetSuite when creating an integration record."
    )
    @JsonSchemaInject(json = """{"order":2,"airbyte_secret":true}""")
    val clientSecret: String,
    @get:JsonProperty("token_id", required = true)
    @param:JsonProperty("token_id", required = true)
    @JsonSchemaTitle("Token ID")
    @JsonPropertyDescription(
        "The token ID used for token-based authentication. " +
            "This is generated in NetSuite when creating a token-based role."
    )
    @JsonSchemaInject(json = """{"order":3}""")
    val tokenId: String,
    @get:JsonProperty("token_secret", required = true)
    @param:JsonProperty("token_secret", required = true)
    @JsonSchemaTitle("Token Secret")
    @JsonPropertyDescription(
        "The token secret used for token-based authentication. " +
            "This is generated in NetSuite when creating a token-based role." +
            "Ensure to keep this value secure."
    )
    @JsonSchemaInject(json = """{"order":4,"airbyte_secret":true}""")
    val tokenSecret: String,
) : AuthenticationMethodConfiguration

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.authentication_method")
class MicronautPropertiesFriendlyAuthenticationMethodConfigurationSpecification {
    var method: String = "password_authentication" // default to password authentication
    var password: String? = null
    // For token-based authentication, these fields will be used
    var clientId: String? = null
    var clientSecret: String? = null
    var tokenId: String? = null
    var tokenSecret: String? = null

    fun asAuthenticationMethodConfiguration(): AuthenticationMethodConfiguration =
        when (method) {
            "password_authentication" -> PasswordAuthentication(password)
            "token_based_authentication" ->
                TokenBasedAuthentication(clientId!!, clientSecret!!, tokenId!!, tokenSecret!!)
            else -> throw ConfigErrorException("invalid value $method")
        }
}
