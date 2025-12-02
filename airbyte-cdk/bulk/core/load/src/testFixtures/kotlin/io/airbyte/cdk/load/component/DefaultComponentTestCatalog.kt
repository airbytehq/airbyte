/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode

/**
 * Utility for creating a default ConfiguredAirbyteCatalog for component tests.
 *
 * Provides a catalog with schema matching ConnectorWiringSuite.createTestRecord():
 * - id: integer
 * - name: string
 * - Airbyte metadata columns
 *
 * Usage in connector test config factory:
 * @Singleton @Primary fun catalog() = DefaultComponentTestCatalog.make()
 */
object DefaultComponentTestCatalog {
    fun make(): ConfiguredAirbyteCatalog {
        val jsonNodeFactory = JsonNodeFactory.instance
        val schema =
            jsonNodeFactory.objectNode().apply {
                put("type", "object")
                set<Nothing>(
                    "properties",
                    jsonNodeFactory.objectNode().apply {
                        set<Nothing>(
                            "id",
                            jsonNodeFactory.objectNode().apply { put("type", "integer") }
                        )
                        set<Nothing>(
                            "name",
                            jsonNodeFactory.objectNode().apply { put("type", "string") }
                        )
                    }
                )
            }

        val stream =
            AirbyteStream()
                .withName("test_stream")
                .withNamespace("test")
                .withJsonSchema(schema)
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH))
                .withSourceDefinedCursor(false)
                .withSourceDefinedPrimaryKey(emptyList())

        val configuredStream =
            ConfiguredAirbyteStream()
                .withStream(stream)
                .withSyncMode(SyncMode.FULL_REFRESH)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withCursorField(emptyList())
                .withPrimaryKey(emptyList())
                .withGenerationId(0L)
                .withMinimumGenerationId(0L)
                .withSyncId(42L)

        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }
}
