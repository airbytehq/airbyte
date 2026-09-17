/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.load.command.DestinationStream
import java.util.UUID

/** Shared run identity for the schema, completion marker, and S3 batch headers. */
internal class S3CopyMetadata(config: S3CopyConfiguration, runId: UUID, epochSeconds: Long) {
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
        stream: DestinationStream,
        descriptor: Map<String, Any>,
        schemaId: String
    ): Map<String, Any> =
        descriptor +
            identity +
            mapOf(
                "schema_id" to schemaId,
                "generation_id" to stream.generationId,
                "sync_id" to stream.syncId,
            )

    /** The catalog sync ID is populated from the platform job ID. */
    fun streamComplete(stream: DestinationStream): Map<String, Any> =
        mapOf<String, Any>("job_id" to stream.syncId) +
            if (stream.minimumGenerationId > 0)
                mapOf("min_generation_id" to stream.minimumGenerationId)
            else emptyMap()

    fun batch(context: CsvCopyContext, recordCount: Int, batchId: UUID): Map<String, String> =
        identity.map { (key, value) -> key.replace('_', '-') to value.toString() }.toMap() +
            mapOf(
                "format-version" to "1",
                "stream-key" to context.streamKey,
                "generation-id" to context.generationId.toString(),
                "sync-id" to context.syncId.toString(),
                "batch-id" to batchId.toString(),
                "schema-id" to context.schemaId,
                "record-count" to recordCount.toString(),
            )
}
