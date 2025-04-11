/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "credential_type"
)
@JsonSubTypes(JsonSubTypes.Type(value = GcsHmacKeySpecification::class, name = "HMAC key"))
sealed class GcsAuthSpecification(
    @JsonSchemaTitle("Credential Type")
    @get:JsonProperty("credential_type")
    val credentialType: Type
) {
    enum class Type(@get:JsonValue val authTypeName: String) {
        HMAC_KEY("HMAC_KEY"),
    }

    abstract fun toGcsAuthConfiguration(): GcsAuthConfiguration
}

@JsonSchemaTitle("HMAC key")
class GcsHmacKeySpecification(
    @get:JsonSchemaTitle("HMAC Access Key")
    @get:JsonPropertyDescription(
        """HMAC key access ID. When linked to a service account, this ID is 61 characters long; when linked to a user account, it is 24 characters long."""
    )
    @get:JsonProperty("hmac_key_access_id")
    @get:JsonSchemaInject(
        json = """{"examples":["1234567890abcdefghij1234"],"airbyte_secret": true, "order": 0}"""
    )
    val accessKeyId: String,
    @get:JsonSchemaTitle("HMAC Secret")
    @get:JsonPropertyDescription(
        """The corresponding secret for the access ID. It is a 40-character base-64 encoded string."""
    )
    @get:JsonProperty("hmac_key_secret")
    @get:JsonSchemaInject(
        json =
            """{"examples":["1234567890abcdefghij1234567890ABCDEFGHIJ"],"airbyte_secret": true, "order": 1}"""
    )
    val secretAccessKey: String,
) : GcsAuthSpecification(Type.HMAC_KEY) {
    override fun toGcsAuthConfiguration(): GcsHmacKeyConfiguration {
        return GcsHmacKeyConfiguration(accessKeyId, secretAccessKey)
    }
}

sealed interface GcsAuthConfiguration

data class GcsHmacKeyConfiguration(val accessKeyId: String, val secretAccessKey: String) :
    GcsAuthConfiguration
