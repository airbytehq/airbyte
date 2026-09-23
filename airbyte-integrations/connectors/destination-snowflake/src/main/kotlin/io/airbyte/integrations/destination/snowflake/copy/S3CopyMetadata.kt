/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.fusion.FusionConfiguration
import io.airbyte.cdk.fusion.FusionMetadata
import io.airbyte.cdk.load.command.DestinationStream
import java.util.UUID

/** Adapts Snowflake's stream and batch context to the shared Fusion contract. */
internal class S3CopyMetadata(config: FusionConfiguration, runId: UUID, epochSeconds: Long) {
    private val metadata = FusionMetadata(config, runId, epochSeconds)

    fun schema(
        stream: DestinationStream,
        descriptor: Map<String, Any?>,
        schemaId: String
    ): Map<String, Any?> = metadata.schema(descriptor, schemaId, stream.generationId, stream.syncId)

    fun streamComplete(stream: DestinationStream): Map<String, Any> =
        metadata.streamComplete(stream.syncId, stream.minimumGenerationId)

    fun batch(context: CsvCopyContext, recordCount: Int, batchId: UUID): Map<String, String> =
        metadata.batch(
            context.streamKey,
            context.generationId,
            context.syncId,
            context.schemaId,
            recordCount.toLong(),
            batchId,
        )
}
