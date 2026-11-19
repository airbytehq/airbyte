/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.fasterxml.jackson.databind.JsonNode
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.util.Jsons
import java.net.URI
import java.net.URISyntaxException

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "credential_type",
)
@JsonSubTypes(JsonSubTypes.Type(value = GcsHmacKeySpecification::class, name = "HMAC_KEY"))
sealed class GcsAuthSpecification(
    @JsonSchemaTitle("Credential Type")
    @get:JsonProperty("credential_type")
    val credentialType: Type = Type.HMAC_KEY,
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
) : GcsAuthSpecification(Type.HMAC_KEY) {
    override fun toGcsAuthConfiguration(): GcsHmacKeyConfiguration {
        return GcsHmacKeyConfiguration(accessKeyId, secretAccessKey)
    }
}

sealed interface GcsAuthConfiguration

data class GcsHmacKeyConfiguration(val accessKeyId: String, val secretAccessKey: String) :
    GcsAuthConfiguration

/**
 * Authenticates with Google Cloud
 * [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
 * instead of an HMAC key.
 *
 * [credentialsJson] is the contents of a credential configuration file (`"type":
 * "external_account"`), as produced by `gcloud iam workload-identity-pools create-cred-config`. It
 * can describe either a federated principal that is granted bucket access directly, or one that
 * impersonates a service account (`service_account_impersonation_url`).
 *
 * The S3-compatible XML API used for HMAC keys cannot carry a federated token, so this
 * configuration makes [io.airbyte.cdk.load.file.gcs.GcsClientFactory] build a
 * [io.airbyte.cdk.load.file.gcs.GcsNativeClient] over the GCS JSON API.
 *
 * Use [fromCredentialsJson] to build one from user input: it validates the document without
 * contacting Google.
 */
data class GcsWorkloadIdentityFederationConfiguration(val credentialsJson: String) :
    GcsAuthConfiguration {
    /** Never print the credential document; it can contain tokens or internal endpoints. */
    override fun toString(): String =
        "GcsWorkloadIdentityFederationConfiguration(credentialsJson=***)"

    companion object {
        const val EXTERNAL_ACCOUNT_TYPE = "external_account"

        /**
         * Validates [credentialsJson] and wraps it. Throws [ConfigErrorException] for anything that
         * isn't a usable `external_account` document.
         *
         * Deliberately does not build `GoogleCredentials` here: for `external_account` that can
         * trigger a live token exchange, so config parsing would depend on network access.
         *
         * Because the credential configuration comes from the user, and it controls which files or
         * URLs the auth library reads the subject token from and where that token is sent, this
         * also enforces the restrictions Google recommends for
         * [externally sourced credential configurations](https://cloud.google.com/docs/authentication/external/externally-sourced-credentials):
         * - the token exchange and impersonation endpoints must be HTTPS `*.googleapis.com` URLs;
         * - executable-sourced credentials are rejected.
         */
        fun fromCredentialsJson(
            credentialsJson: String,
        ): GcsWorkloadIdentityFederationConfiguration {
            if (credentialsJson.isBlank()) {
                throw ConfigErrorException(
                    "Workload Identity Federation requires a credential configuration (credentials_json).",
                )
            }
            val parsed: JsonNode =
                try {
                    Jsons.readTree(credentialsJson)
                } catch (e: Exception) {
                    // Don't echo the parser message: it can quote parts of the secret.
                    throw ConfigErrorException(
                        "The Workload Identity Federation credential configuration is not valid JSON.",
                    )
                }
            if (!parsed.isObject) {
                throw ConfigErrorException(
                    "The Workload Identity Federation credential configuration must be a JSON object.",
                )
            }

            val type = parsed.get("type")?.takeIf { it.isTextual }?.asText()
            if (type != EXTERNAL_ACCOUNT_TYPE) {
                throw ConfigErrorException(
                    "The credential configuration must have \"type\": \"$EXTERNAL_ACCOUNT_TYPE\" " +
                        "(a Workload Identity Federation credential configuration file), but found " +
                        (type?.let { "\"$it\"" } ?: "no \"type\" field") +
                        ". Service account keys are not supported here.",
                )
            }
            for (field in listOf("audience", "subject_token_type", "credential_source")) {
                if (parsed.get(field) == null || parsed.get(field).isNull) {
                    throw ConfigErrorException(
                        "The Workload Identity Federation credential configuration is missing " +
                            "the required \"$field\" field.",
                    )
                }
            }
            if (parsed.get("credential_source").has("executable")) {
                throw ConfigErrorException(
                    "Executable-sourced Workload Identity Federation credentials are not " +
                        "supported. Use a file, URL or AWS credential source instead.",
                )
            }
            for (field in GOOGLE_ENDPOINT_FIELDS) {
                val value = parsed.get(field)?.takeUnless { it.isNull } ?: continue
                if (!value.isTextual || !isGoogleApisHttpsUrl(value.asText())) {
                    throw ConfigErrorException(
                        "The \"$field\" in the Workload Identity Federation credential " +
                            "configuration must be an https://*.googleapis.com URL.",
                    )
                }
            }
            return GcsWorkloadIdentityFederationConfiguration(credentialsJson)
        }

        /** Fields naming Google endpoints the auth library sends tokens to. */
        private val GOOGLE_ENDPOINT_FIELDS =
            listOf("token_url", "service_account_impersonation_url", "token_info_url")

        private fun isGoogleApisHttpsUrl(url: String): Boolean {
            val uri =
                try {
                    URI(url)
                } catch (_: URISyntaxException) {
                    return false
                }
            val host = uri.host?.lowercase() ?: return false
            return uri.scheme.equals("https", ignoreCase = true) &&
                uri.userInfo == null &&
                host.endsWith(".googleapis.com")
        }
    }
}
