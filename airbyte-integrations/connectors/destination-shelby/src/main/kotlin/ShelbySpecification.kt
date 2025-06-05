package io.airbyte.integrations.destination.shelby

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class ShelbySpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Client ID")
    @get:JsonPropertyDescription(
        """Enter your Salesforce developer application's <a href="https://developer.salesforce.com/forums/?id=9062I000000DLgbQAG">Client ID</a>.""",
    )
    @get:JsonProperty("client_id")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val clientId: String = ""

    @get:JsonSchemaTitle("Client Secret")
    @get:JsonPropertyDescription(
        """Enter your Salesforce developer application's <a href="https://developer.salesforce.com/forums/?id=9062I000000DLgbQAG">Client secret</a>.""",
    )
    @get:JsonProperty("client_secret")
    @get:JsonSchemaInject(json = """{"order": 1, "airbyte_secret": true}""")
    val clientSecret: String = ""

    @get:JsonSchemaTitle("Refresh Token")
    @get:JsonPropertyDescription(
        """Enter your application's <a href="https://developer.salesforce.com/docs/atlas.en-us.mobile_sdk.meta/mobile_sdk/oauth_refresh_token_flow.htm">Salesforce Refresh Token</a> used for Airbyte to access your Salesforce account.""",
    )
    @get:JsonProperty("refresh_token")
    @get:JsonSchemaInject(json = """{"order": 2, "airbyte_secret": true}""")
    val refreshToken: String = ""

    @get:JsonSchemaTitle("Is Sandbox")
    @get:JsonPropertyDescription(
        """Toggle if you're using a <a href="https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5">Salesforce Sandbox</a>.""",
    )
    @get:JsonProperty("is_sandbox")
    @get:JsonSchemaInject(json = """{"order": 3, "default": false}""")
    val isSandbox: Boolean = false

    @get:JsonProperty("Auth Type")
    @get:JsonSchemaInject(json = """{"const": "Client"}""")
    val authType: String = ""
}

@Singleton
class ShelbySpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
