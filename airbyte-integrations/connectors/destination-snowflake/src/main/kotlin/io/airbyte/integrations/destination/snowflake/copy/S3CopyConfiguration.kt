package io.airbyte.integrations.destination.snowflake.copy

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
) {
    companion object {
        private fun required(name: String): String =
            System.getenv(name)?.takeIf { it.isNotBlank() }
                ?: error("$name is required when AIRBYTE_S3_COPY_ENABLED=true")

        fun fromEnvironment(): S3CopyConfiguration? {
            val enabled = System.getenv("AIRBYTE_S3_COPY_ENABLED") ?: "false"
            require(enabled == "true" || enabled == "false") {
                "AIRBYTE_S3_COPY_ENABLED must be true or false"
            }
            if (enabled != "true") return null
            val prefix = (System.getenv("AIRBYTE_S3_COPY_PREFIX") ?: "fusion")
                .trim('/')
            require(prefix.isNotEmpty()) { "AIRBYTE_S3_COPY_PREFIX must not be empty" }
            return S3CopyConfiguration(
                roleArn = required("AIRBYTE_S3_COPY_ROLE_ARN"),
                bucket = required("AIRBYTE_S3_COPY_BUCKET"),
                region = required("AIRBYTE_S3_COPY_REGION"),
                connectionId = UUID.fromString(required("AIRBYTE_S3_COPY_CONNECTION_ID")),
                workspaceId = UUID.fromString(required("AIRBYTE_S3_COPY_WORKSPACE_ID")),
                sourceId = UUID.fromString(required("AIRBYTE_S3_COPY_SOURCE_ID")),
                prefix = prefix,
                externalId = System.getenv("AIRBYTE_S3_COPY_EXTERNAL_ID")?.takeIf { it.isNotBlank() },
            )
        }
    }
}
