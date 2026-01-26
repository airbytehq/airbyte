/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Test
import java.util.Collections

class SafeDestinationCatalogFactoryTest {

    @Test
    fun `test syncCatalog with APPEND_DEDUP and null PK cursor does not throw NPE`() {
        val factory = SafeDestinationCatalogFactory()
        
        val stream = ConfiguredAirbyteStream()
            .withStream(AirbyteStream().withName("test").withNamespace("ns").withJsonSchema(mockk(relaxed = true)))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withSyncMode(SyncMode.INCREMENTAL)
            .withPrimaryKey(null)
            .withCursorField(null)
            .withGenerationId(1L)
            .withMinimumGenerationId(1L)
            .withSyncId(1L)
            
        val catalog = ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(stream))
        val namespaceMapper = mockk<NamespaceMapper>(relaxed = true)
        val jsonSchemaConverter = mockk<JsonSchemaToAirbyteType>(relaxed = true)
        
        // Mock the convert method
        every { jsonSchemaConverter.convert(any()) } returns mockk(relaxed=true)

        assertDoesNotThrow {
            val destCatalog = factory.syncCatalog(
                catalog, 
                namespaceMapper, 
                jsonSchemaConverter
            )
            val importType = destCatalog.streams.first().importType
            assert(importType is Dedupe)
            val dedupe = importType as Dedupe
            assert(dedupe.primaryKey.isEmpty())
            assert(dedupe.cursor.isEmpty())
        }
    }

    @Test
    fun `test checkCatalog returns test stream`() {
        val factory = SafeDestinationCatalogFactory()
        val namespaceMapper = mockk<NamespaceMapper>(relaxed = true)
        
        val destCatalog = factory.checkCatalog(
            namespaceMapper,
            "custom_check_ns"
        )
        
        assertEquals(1, destCatalog.streams.size)
        assertEquals("custom_check_ns", destCatalog.streams.first().unmappedNamespace)
        assert(destCatalog.streams.first().unmappedName.startsWith("test"))
    }
}
