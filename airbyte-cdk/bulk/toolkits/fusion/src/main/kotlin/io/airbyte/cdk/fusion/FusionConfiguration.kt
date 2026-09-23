/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.fusion

import java.util.UUID

/**
 * Fusion is enabled and configured solely by the platform environment.
 *
 * AWS clients also read standard SDK settings directly from the process environment. For local
 * testing, injected AWS_ENDPOINT_URL (all services), AWS_ENDPOINT_URL_S3, and AWS_ENDPOINT_URL_STS
 * automatically configure client endpoints; they do not need fields or parsing here. Service-specific
 * endpoint variables take precedence over AWS_ENDPOINT_URL. Passing these settings only in the map
 * supplied to fromEnvironment does not configure the clients.
 */
class FusionConfiguration(
    val roleArn: String,
    val bucket: String,
    val region: String,
    val connectionId: UUID,
    val workspaceId: UUID,
    val sourceId: UUID,
    val prefix: String,
    val externalId: String?,
    val organizationId: UUID,
    val destinationId: UUID,
    val accessKeyId: String? = null,
    val secretAccessKey: String? = null,
) {
    init {
        require((accessKeyId == null) == (secretAccessKey == null)) {
            "AWS_ASSUME_ROLE_ACCESS_KEY_ID and AWS_ASSUME_ROLE_SECRET_ACCESS_KEY must be provided together"
        }
    }

    companion object {
        @JvmStatic
        fun fromEnvironment(env: Map<String, String>): FusionConfiguration? {
            val enabled = env["AIRBYTE_S3_COPY_ENABLED"] ?: "false"
            require(enabled == "true" || enabled == "false") {
                "AIRBYTE_S3_COPY_ENABLED must be true or false"
            }
            if (enabled != "true") return null
            fun required(name: String): String =
                env[name]?.takeIf { it.isNotBlank() }
                    ?: error("$name is required when AIRBYTE_S3_COPY_ENABLED=true")
            fun id(name: String): UUID {
                val envName = "AIRBYTE_${name}_ID"
                val value = required(envName)
                val parsed = runCatching { UUID.fromString(value) }.getOrNull()
                require(parsed != null && parsed.toString().equals(value, ignoreCase = true)) {
                    "$envName must be a canonical UUID"
                }
                return parsed
            }
            val prefix = (env["AIRBYTE_S3_COPY_PREFIX"] ?: "fusion").trim('/')
            require(prefix.isNotBlank()) { "AIRBYTE_S3_COPY_PREFIX must not be empty" }
            return FusionConfiguration(
                roleArn = required("AIRBYTE_S3_COPY_ROLE_ARN"),
                bucket = required("AIRBYTE_S3_COPY_BUCKET"),
                region = required("AIRBYTE_S3_COPY_REGION"),
                connectionId = id("CONNECTION"),
                workspaceId = id("WORKSPACE"),
                sourceId = id("SOURCE"),
                prefix = prefix,
                externalId = env["AWS_ASSUME_ROLE_EXTERNAL_ID"]?.takeIf { it.isNotBlank() },
                organizationId = id("ORGANIZATION"),
                destinationId = id("DESTINATION"),
                accessKeyId = env["AWS_ASSUME_ROLE_ACCESS_KEY_ID"]?.takeIf { it.isNotBlank() },
                secretAccessKey =
                    env["AWS_ASSUME_ROLE_SECRET_ACCESS_KEY"]?.takeIf { it.isNotBlank() },
            )
        }
    }
}
