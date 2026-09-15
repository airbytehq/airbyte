/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import java.util.UUID

/**
 * Internal, process-latched routing. The caller must gate spec/check before parsing this config.
 */
data class S3CopyConfiguration(
    val bucket: String,
    val region: String,
    val roleArn: String,
    val workspaceId: UUID,
    val sourceId: UUID,
    val connectionId: UUID,
    val prefix: String = "fusion",
    val externalId: String? = null,
    val organizationId: UUID = UUID(0, 0),
    val destinationId: UUID = UUID(0, 0),
) {
    companion object {
        /**
         * TEMPORARY: force the preview route at the write factory boundary. Runtime config IDs
         * override environment IDs; absent IDs are parsed as the zero UUID.
         */
        fun previewEnvironment(
            config: BigqueryConfiguration,
            env: Map<String, String> = System.getenv(),
        ): Map<String, String> =
            env +
                mapOf(
                    "AIRBYTE_S3_COPY_ENABLED" to "true",
                    "AIRBYTE_S3_COPY_BUCKET" to "airbyte-fusion-context-store",
                    "AIRBYTE_S3_COPY_REGION" to "us-west-2",
                    "AIRBYTE_S3_COPY_ROLE_ARN" to
                        "arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy",
                    "AIRBYTE_S3_COPY_PREFIX" to "fusion",
                ) +
                listOf(
                        "AIRBYTE_S3_COPY_ORGANIZATION_ID" to config.organizationId,
                        "AIRBYTE_S3_COPY_WORKSPACE_ID" to config.workspaceId,
                        "AIRBYTE_S3_COPY_SOURCE_ID" to config.sourceId,
                        "AIRBYTE_S3_COPY_CONNECTION_ID" to config.connectionId,
                        "AIRBYTE_S3_COPY_DESTINATION_ID" to config.destinationId,
                    )
                    .mapNotNull { (key, value) -> value?.let { key to it } }
                    .toMap()

        /** Pure parsing: enablement defaults to false and all five routing IDs are optional. */
        fun fromEnvironment(env: Map<String, String> = System.getenv()): S3CopyConfiguration? {
            when (env["AIRBYTE_S3_COPY_ENABLED"] ?: "false") {
                "false" -> return null
                "true" -> Unit
                else -> error("AIRBYTE_S3_COPY_ENABLED must be exactly true or false")
            }

            fun required(suffix: String): String {
                val name = "AIRBYTE_S3_COPY_$suffix"
                return env[name]?.takeIf { it.isNotBlank() && it == it.trim() }
                    ?: error("$name is required and must not contain surrounding whitespace")
            }

            fun uuid(suffix: String): UUID {
                val value = env["AIRBYTE_S3_COPY_$suffix"] ?: return UUID(0, 0)
                val parsed = runCatching { UUID.fromString(value) }.getOrNull()
                check(parsed != null && parsed.toString().equals(value, ignoreCase = true)) {
                    "AIRBYTE_S3_COPY_$suffix must be a canonical UUID"
                }
                return parsed
            }

            val prefix = (env["AIRBYTE_S3_COPY_PREFIX"] ?: "fusion").trim('/')
            check(prefix.isNotBlank() && prefix == prefix.trim()) {
                "AIRBYTE_S3_COPY_PREFIX must be nonempty after trimming surrounding slashes"
            }
            val externalId = env["AIRBYTE_S3_COPY_EXTERNAL_ID"]
            check(
                externalId == null || (externalId.isNotBlank() && externalId == externalId.trim())
            ) { "AIRBYTE_S3_COPY_EXTERNAL_ID must be nonblank when supplied" }
            return S3CopyConfiguration(
                bucket = required("BUCKET"),
                region = required("REGION"),
                roleArn = required("ROLE_ARN"),
                workspaceId = uuid("WORKSPACE_ID"),
                sourceId = uuid("SOURCE_ID"),
                connectionId = uuid("CONNECTION_ID"),
                prefix = prefix,
                externalId = externalId,
                organizationId = uuid("ORGANIZATION_ID"),
                destinationId = uuid("DESTINATION_ID"),
            )
        }
    }
}
