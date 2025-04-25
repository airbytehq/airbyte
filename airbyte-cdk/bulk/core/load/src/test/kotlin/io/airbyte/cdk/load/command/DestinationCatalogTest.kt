/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DestinationCatalogTest {
    @Test
    fun roundTrip() {
        val originalCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withIncludeFiles(false)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                    .withNamespace("namespace1")
                                    .withName("name1")
                                    .withIsFileBased(false)
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withIncludeFiles(true)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                    .withNamespace("namespace2")
                                    .withName("name2")
                                    .withIsFileBased(true)
                            )
                            .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                            .withCursorField(listOf("cursor")),
                        ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withIncludeFiles(false)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                    .withNamespace("namespace3")
                                    .withName("name3")
                                    .withIsFileBased(false)
                            ),
                       ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withIncludeFiles(false)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema("""{"type": "object"}""".deserializeToNode())
                                    .withNamespace("namespace4")
                                    .withName("name4")
                                    .withIsFileBased(true)
                            )
                            .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                            .withCursorField(listOf("cursor")),
                    ),
                )

        val streamFactory =
            DestinationStreamFactory(
                JsonSchemaToAirbyteType(JsonSchemaToAirbyteType.UnionBehavior.DEFAULT)
            )
        val catalogFactory = DefaultDestinationCatalogFactory(originalCatalog, streamFactory)
        val destinationCatalog = catalogFactory.make()
        assertEquals(originalCatalog, destinationCatalog.asProtocolObject())
    }
}
