/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.util.UUID

data class S3CopyConfiguration(
    val roleArn: String,
    val bucket: String,
    val region: String,
    val connectionId: UUID,
    val workspaceId: UUID,
    val sourceId: UUID,
    val prefix: String,
    val externalId: String?,
    val organizationId: UUID = UUID(0, 0),
    val destinationId: UUID = UUID(0, 0),
) {
    companion object {
        /** TEMPORARY: force the preview route only at the write factory boundary. */
        fun previewEnvironment(env: Map<String, String>): Map<String, String> =
            env +
                mapOf(
                    "AIRBYTE_S3_COPY_ENABLED" to "true",
                    "AIRBYTE_S3_COPY_BUCKET" to "airbyte-fusion-context-store",
                    "AIRBYTE_S3_COPY_REGION" to "us-west-2",
                    "AIRBYTE_S3_COPY_ROLE_ARN" to
                        "arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy",
                    "AIRBYTE_S3_COPY_PREFIX" to "fusion",
                )

        /** Pure parsing: config IDs override environment IDs, then fall back to the zero UUID. */
        fun fromEnvironment(
            spec: SnowflakeSpecification,
            env: Map<String, String>
        ): S3CopyConfiguration? {
            val enabled = env["AIRBYTE_S3_COPY_ENABLED"] ?: "false"
            require(enabled == "true" || enabled == "false") {
                "AIRBYTE_S3_COPY_ENABLED must be true or false"
            }
            if (enabled != "true") return null
            fun required(name: String): String =
                env[name]?.takeIf { it.isNotBlank() }
                    ?: error("$name is required when AIRBYTE_S3_COPY_ENABLED=true")
            fun id(name: String, override: String?): UUID {
                val envName = "AIRBYTE_${name.uppercase()}_ID"
                val value = override ?: env[envName] ?: return UUID(0, 0)
                val parsed = runCatching { UUID.fromString(value) }.getOrNull()
                require(parsed != null && parsed.toString().equals(value, ignoreCase = true)) {
                    "${name}_id / $envName must be a canonical UUID"
                }
                return parsed
            }
            val prefix = (env["AIRBYTE_S3_COPY_PREFIX"] ?: "fusion").trim('/')
            require(prefix.isNotBlank()) { "AIRBYTE_S3_COPY_PREFIX must not be empty" }
            return S3CopyConfiguration(
                roleArn = required("AIRBYTE_S3_COPY_ROLE_ARN"),
                bucket = required("AIRBYTE_S3_COPY_BUCKET"),
                region = required("AIRBYTE_S3_COPY_REGION"),
                connectionId = id("connection", spec.connectionId),
                workspaceId = id("workspace", spec.workspaceId),
                sourceId = id("source", spec.sourceId),
                prefix = prefix,
                externalId = env["AIRBYTE_S3_COPY_EXTERNAL_ID"]?.takeIf { it.isNotBlank() },
                organizationId = id("organization", spec.organizationId),
                destinationId = id("destination", spec.destinationId),
            )
        }
    }
}
