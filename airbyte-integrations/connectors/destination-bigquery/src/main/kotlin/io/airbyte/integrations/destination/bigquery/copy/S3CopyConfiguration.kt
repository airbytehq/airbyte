/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

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
) {
    companion object {
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
                val value = required(suffix)
                val parsed = runCatching { UUID.fromString(value) }.getOrNull()
                check(parsed != null && parsed.toString() == value) {
                    "AIRBYTE_S3_COPY_$suffix must be a canonical lowercase UUID"
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
            )
        }
    }
}
