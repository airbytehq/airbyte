/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface GcsHmacKeySpecification {
    @get:JsonSchemaTitle("HMAC Access Key")
    @get:JsonPropertyDescription(
        """HMAC key access ID. When linked to a service account, this ID is 61 characters long; when linked to a user account, it is 24 characters long."""
    )
    @get:JsonProperty("hmac_key_access_id")
    @get:JsonSchemaInject(
        json =
            """{"examples":["1234567890abcdefghij1234"],"airbyte_secret": true,"always_show": true}"""
    )
    val accessKeyId: String

    @get:JsonSchemaTitle("HMAC Secret")
    @get:JsonPropertyDescription(
        """The corresponding secret for the access ID. It is a 40-character base-64 encoded string."""
    )
    @get:JsonProperty("hmac_key_secret")
    @get:JsonSchemaInject(
        json =
            """{"examples":["1234567890abcdefghij1234567890ABCDEFGHIJ"],"airbyte_secret": true,"always_show": true}"""
    )
    val secretAccessKey: String

    fun toGcsHmacKeyConfiguration(): GcsHmacKeyConfiguration {
        return GcsHmacKeyConfiguration(accessKeyId, secretAccessKey)
    }
}

data class GcsHmacKeyConfiguration(val accessKeyId: String, val secretAccessKey: String)

interface GcsHmacKeyConfigurationProvider {
    val hmacKeyConfiguration: GcsHmacKeyConfiguration
}
