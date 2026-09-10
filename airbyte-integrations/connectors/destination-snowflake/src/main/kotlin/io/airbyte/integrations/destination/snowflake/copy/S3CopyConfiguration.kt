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
        fun fromEnvironment(): S3CopyConfiguration? {
            // TEMPORARY: force archive copying for the Fusion preview. Revert before merge.
            val enabled = "true"
            require(enabled == "true" || enabled == "false") {
                "AIRBYTE_S3_COPY_ENABLED must be true or false"
            }
            if (enabled != "true") return null
            val prefix = "fusion"
            require(prefix.isNotEmpty()) { "AIRBYTE_S3_COPY_PREFIX must not be empty" }
            return S3CopyConfiguration(
                roleArn = "arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy",
                bucket = "sonar-entity-cache",
                region = "us-east-2",
                // TEMPORARY: nil actor IDs for the Fusion preview image. Revert before merge.
                connectionId = UUID(0, 0),
                workspaceId = UUID(0, 0),
                sourceId = UUID(0, 0),
                prefix = prefix,
                externalId = null,
            )
        }
    }
}
