/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.protocol.models.Jsons
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
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema(Jsons.deserialize("""{"type": "object"}"""))
                                    .withNamespace("namespace1")
                                    .withName("name1")
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema(Jsons.deserialize("""{"type": "object"}"""))
                                    .withNamespace("namespace2")
                                    .withName("name2")
                            )
                            .withPrimaryKey(listOf(listOf("id1"), listOf("id2")))
                            .withCursorField(listOf("cursor")),
                        ConfiguredAirbyteStream()
                            .withSyncId(12)
                            .withMinimumGenerationId(34)
                            .withGenerationId(56)
                            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                            .withStream(
                                AirbyteStream()
                                    .withJsonSchema(Jsons.deserialize("""{"type": "object"}"""))
                                    .withNamespace("namespace3")
                                    .withName("name3")
                            ),
                    ),
                )

        val streamFactory = DestinationStreamFactory()
        val catalogFactory = DefaultDestinationCatalogFactory(originalCatalog, streamFactory)
        val destinationCatalog = catalogFactory.make()
        assertEquals(originalCatalog, destinationCatalog.asProtocolObject())
    }
}
