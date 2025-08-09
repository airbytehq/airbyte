/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.dlq.ConfigurationSpecificationWithDlq
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

enum class CredentialsType(@get:JsonValue val type: String) {
    OAuth("OAuth Credentials"),
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = OAuthCredentialsSpec::class, name = "OAuth"),
)
sealed interface CredentialsSpec {
    @get:JsonSchemaTitle("Credentials")
    @get:JsonProperty("type")
    val credentialsType: CredentialsType
}

class OAuthCredentialsSpec : CredentialsSpec {
    override val credentialsType = CredentialsType.OAuth

    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription(
        "The Client ID of your HubSpot developer application. See the <a href=\\\"https://legacydocs.hubspot.com/docs/methods/oauth2/oauth2-quickstart\\\">Hubspot docs</a> if you need help finding this ID.",
    )
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(json = """{"order": 0, "airbyte_secret": true}""")
    val clientId: String = ""

    @get:JsonSchemaTitle("Client Secret")
    @get:JsonPropertyDescription(
        "The client secret for your HubSpot developer application. See the <a href=\\\"https://legacydocs.hubspot.com/docs/methods/oauth2/oauth2-quickstart\\\">Hubspot docs</a> if you need help finding this secret.",
    )
    @get:JsonProperty("client_secret")
    @get:JsonSchemaInject(json = """{"order": 1, "airbyte_secret": true}""")
    val clientSecret: String = ""

    @get:JsonSchemaTitle("Refresh Token")
    @get:JsonPropertyDescription(
        "Refresh token to renew an expired access token. See the <a href=\\\"https://legacydocs.hubspot.com/docs/methods/oauth2/oauth2-quickstart\\\">Hubspot docs</a> if you need help finding this token.",
    )
    @get:JsonProperty("refresh_token")
    @get:JsonSchemaInject(json = """{"order": 2, "airbyte_secret": true}""")
    val refreshToken: String = ""
}

@Singleton
class HubSpotSpecification : ConfigurationSpecificationWithDlq() {
    @get:JsonSchemaTitle("Credentials")
    @get:JsonPropertyDescription("""Choose how to authenticate to HubSpot.""")
    @get:JsonProperty("credentials")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val credentials: CredentialsSpec = OAuthCredentialsSpec()
}

@Singleton
class HubSpotSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
