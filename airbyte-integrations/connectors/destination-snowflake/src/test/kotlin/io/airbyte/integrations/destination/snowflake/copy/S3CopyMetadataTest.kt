/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.fusion.FusionConfiguration
import io.airbyte.cdk.fusion.FusionPaths
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.util.Jsons
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class S3CopyMetadataTest {
    @Test
    fun `schemas and batch headers carry the same full run identity`() {
        val config =
            FusionConfiguration(
                "role",
                "bucket",
                "region",
                UUID(0, 4),
                UUID(0, 2),
                UUID(0, 3),
                "fusion",
                null,
                UUID(0, 1),
                UUID(0, 5)
            )
        val runId = UUID(0, 6)
        val epochSeconds = 1789400000L
        val metadata = S3CopyMetadata(config, runId, epochSeconds)
        val stream =
            mockk<DestinationStream> {
                every { generationId } returns 42L
                every { minimumGenerationId } returns 42L
                every { syncId } returns 12345L
                every { unmappedNamespace } returns "public"
                every { unmappedName } returns "Orders/日本"
                every { mappedDescriptor } returns
                    DestinationStream.Descriptor("analytics", "ORDERS")
            }
        val path = FusionPaths.run(config, stream.unmappedName, runId, epochSeconds)
        val context =
            CsvCopyContext(
                "stream-hash",
                42,
                12345,
                "schema-hash",
                runId,
                config.connectionId,
                path,
                epochSeconds
            )
        val schema =
            metadata.schema(
                stream,
                mapOf(
                    "columns" to emptyMap<String, Any>(),
                    "source_schema" to emptyMap<String, Any>(),
                    "primary_key" to emptyList<Any>(),
                    "cursor" to emptyList<String>()
                ),
                "schema-hash"
            )
        val complete = metadata.streamComplete(stream)
        val batchId = UUID(0, 7)
        val headers = metadata.batch(context, 19, batchId)
        val expected =
            mapOf(
                "organization_id" to config.organizationId,
                "workspace_id" to config.workspaceId,
                "source_id" to config.sourceId,
                "connection_id" to config.connectionId,
                "destination_id" to config.destinationId,
                "run_id" to runId,
                "epoch_seconds" to epochSeconds,
            )
        expected.forEach { (key, value) ->
            assertEquals(value, schema[key])
            assertEquals(value.toString(), headers[key.replace('_', '-')])
        }
        assertEquals(mapOf("job_id" to 12345L, "min_generation_id" to 42L), complete)
        every { stream.minimumGenerationId } returns 0L
        assertEquals(mapOf("job_id" to 12345L), metadata.streamComplete(stream))
        assertEquals(42L, schema["generation_id"])
        assertEquals(12345L, schema["sync_id"])
        assertEquals("schema-hash", schema["schema_id"])
        assertEquals("schema-hash", headers["schema-id"])
        assertEquals("42", headers["generation-id"])
        assertEquals("12345", headers["sync-id"])
        assertEquals("19", headers["record-count"])
        assertEquals(batchId.toString(), headers["batch-id"])
        assertEquals(headers, metadata.batch(context, 19, batchId))
        assertTrue(
            headers.entries.sumOf { (key, value) ->
                (key + value).toByteArray(Charsets.UTF_8).size
            } < 2048
        )
        // UUIDs and the numeric epoch must also survive serialization to the JSON sidecars.
        val json = String(Jsons.writeValueAsBytes(schema), Charsets.UTF_8)
        assertTrue(json.contains("\"epoch_seconds\":$epochSeconds"))
        assertTrue(json.contains("\"organization_id\":\"${config.organizationId}\""))
    }
}
