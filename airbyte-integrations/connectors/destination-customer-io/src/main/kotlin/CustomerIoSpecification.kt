/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.dlq.ConfigurationSpecificationWithDlq
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class CustomerIoSpecification : ConfigurationSpecificationWithDlq() {
    @get:JsonSchemaTitle("Credentials")
    @get:JsonPropertyDescription(
        """Enter the site ID and API key to authenticate.""",
    )
    @get:JsonProperty("credentials")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val credentials: CustomerIoCredentialsSpecification = CustomerIoCredentialsSpecification()
}

//
class CustomerIoCredentialsSpecification {
    @get:JsonSchemaTitle("Site ID")
    @get:JsonPropertyDescription(
        """Enter your Customer IO <a href="https://docs.customer.io/integrations/sdk/ios/getting-started/auth/#get-your-api-key">Site ID</a>.""",
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true,"always_show": true,"order":1}""")
    val siteId: String = ""

    @get:JsonSchemaTitle("API Key")
    @get:JsonPropertyDescription(
        """Enter your Customer IO <a href="https://docs.customer.io/integrations/sdk/ios/getting-started/auth/#get-your-api-key">API Key</a>.""",
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true,"always_show": true,"order":2}""")
    val apiKey: String = ""
}

@Singleton
class CustomerIoSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
