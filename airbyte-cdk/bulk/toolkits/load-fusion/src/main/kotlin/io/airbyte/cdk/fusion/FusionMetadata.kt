/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.fusion

import java.util.UUID

/** Shared run identity for the schema, completion marker, and S3 batch headers. */
class FusionMetadata(config: FusionConfiguration, runId: UUID, epochSeconds: Long) {
    private val identity =
        mapOf(
            "organization_id" to config.organizationId,
            "workspace_id" to config.workspaceId,
            "source_id" to config.sourceId,
            "connection_id" to config.connectionId,
            "destination_id" to config.destinationId,
            "run_id" to runId,
            "epoch_seconds" to epochSeconds,
        )

    fun schema(
        descriptor: Map<String, Any?>,
        schemaId: String,
        generationId: Long,
        syncId: Long
    ): Map<String, Any?> {
        require(listOf("source_schema", "primary_key", "cursor").all { descriptor[it] != null }) {
            "Fusion schema descriptor must include source_schema, primary_key, and cursor"
        }
        return descriptor +
            identity +
            mapOf(
                "schema_id" to schemaId,
                "generation_id" to generationId,
                "sync_id" to syncId,
            )
    }

    /** The catalog sync ID is populated from the platform job ID. */
    @JvmOverloads
    fun streamComplete(jobId: Long, minGenerationId: Long? = null): Map<String, Any> =
        mapOf<String, Any>("job_id" to jobId) +
            if (minGenerationId != null && minGenerationId >= 0)
                mapOf("min_generation_id" to minGenerationId)
            else emptyMap()

    fun batch(
        streamKey: String,
        generationId: Long,
        syncId: Long,
        schemaId: String,
        recordCount: Long,
        batchId: UUID,
    ): Map<String, String> =
        identity.map { (key, value) -> key.replace('_', '-') to value.toString() }.toMap() +
            mapOf(
                "format-version" to "1",
                "stream-key" to streamKey,
                "generation-id" to generationId.toString(),
                "sync-id" to syncId.toString(),
                "batch-id" to batchId.toString(),
                "schema-id" to schemaId,
                "record-count" to recordCount.toString(),
            )
}
