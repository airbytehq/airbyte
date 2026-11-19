/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.gcs.GcsAuthConfiguration
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsWorkloadIdentityFederationConfiguration

/**
 * The `credential` dropdown.
 *
 * Mirrors the CDK's `GcsAuthSpecification` (same `credential_type` discriminator and HMAC field
 * names, so existing HMAC configs deserialize unchanged) and adds Workload Identity Federation. It
 * lives in the connector because the CDK's class is sealed and shared with destination-bigquery,
 * whose spec should not gain a WIF option.
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "credential_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = GcsV2HmacKeySpecification::class, name = "HMAC_KEY"),
    JsonSubTypes.Type(
        value = GcsV2WorkloadIdentityFederationSpecification::class,
        name = "WORKLOAD_IDENTITY_FEDERATION",
    ),
)
sealed class GcsV2AuthSpecification(
    @JsonSchemaTitle("Credential Type")
    @get:JsonProperty("credential_type")
    val credentialType: Type,
) {
    enum class Type(@get:JsonValue val authTypeName: String) {
        HMAC_KEY("HMAC_KEY"),
        WORKLOAD_IDENTITY_FEDERATION("WORKLOAD_IDENTITY_FEDERATION"),
    }

    abstract fun toGcsAuthConfiguration(): GcsAuthConfiguration
}

@JsonSchemaTitle("HMAC key")
class GcsV2HmacKeySpecification(
    @get:JsonSchemaTitle("HMAC Access Key")
    @get:JsonPropertyDescription(
        """HMAC key access ID. When linked to a service account, this ID is 61 characters long; when linked to a user account, it is 24 characters long.""",
    )
    @get:JsonProperty("hmac_key_access_id")
    @get:JsonSchemaInject(
        json = """{"examples":["1234567890abcdefghij1234"],"airbyte_secret": true, "order": 0}""",
    )
    val accessKeyId: String,
    @get:JsonSchemaTitle("HMAC Secret")
    @get:JsonPropertyDescription(
        """The corresponding secret for the access ID. It is a 40-character base-64 encoded string.""",
    )
    @get:JsonProperty("hmac_key_secret")
    @get:JsonSchemaInject(
        json =
            """{"examples":["1234567890abcdefghij1234567890ABCDEFGHIJ"],"airbyte_secret": true, "order": 1}""",
    )
    val secretAccessKey: String,
) : GcsV2AuthSpecification(Type.HMAC_KEY) {
    override fun toGcsAuthConfiguration(): GcsHmacKeyConfiguration {
        if (accessKeyId.isBlank() || secretAccessKey.isBlank()) {
            throw ConfigErrorException(
                "HMAC key authentication requires both an access key and a secret.",
            )
        }
        return GcsHmacKeyConfiguration(accessKeyId, secretAccessKey)
    }
}

/**
 * Writes go through the native GCS JSON API rather than the S3-compatible XML API, which cannot
 * carry a federated token.
 */
@JsonSchemaTitle("Workload Identity Federation")
class GcsV2WorkloadIdentityFederationSpecification(
    @get:JsonSchemaTitle("Credential Configuration")
    @get:JsonPropertyDescription(
        """Contents of a <a href="https://cloud.google.com/iam/docs/workload-identity-federation">Workload Identity Federation</a> credential configuration file (<code>"type": "external_account"</code>), as created by <code>gcloud iam workload-identity-pools create-cred-config</code>. Service account keys are not accepted.""",
    )
    @get:JsonProperty("credentials_json")
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "multiline": true, "order": 0}""")
    val credentialsJson: String,
) : GcsV2AuthSpecification(Type.WORKLOAD_IDENTITY_FEDERATION) {
    override fun toGcsAuthConfiguration(): GcsWorkloadIdentityFederationConfiguration =
        GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(credentialsJson)
}
