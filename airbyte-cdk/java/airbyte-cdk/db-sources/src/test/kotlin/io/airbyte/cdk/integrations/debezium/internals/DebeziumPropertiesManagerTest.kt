/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.Properties
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

internal class DebeziumPropertiesManagerTest {
    @Test
    fun `preserves explicit Debezium queue and batch sizes`() {
        val configuredProperties =
            Properties().apply {
                setProperty("max.queue.size", "8")
                setProperty("max.batch.size", "8")
            }
        val manager =
            object :
                DebeziumPropertiesManager(
                    configuredProperties,
                    ObjectMapper().createObjectNode(),
                    ConfiguredAirbyteCatalog(),
                    emptyList(),
                ) {
                override fun getConnectionConfiguration(
                    config: com.fasterxml.jackson.databind.JsonNode,
                ) = Properties()

                override fun getName(config: com.fasterxml.jackson.databind.JsonNode) = "test"

                override fun getIncludeConfiguration(
                    catalog: ConfiguredAirbyteCatalog,
                    config: com.fasterxml.jackson.databind.JsonNode?,
                    streamNames: List<String>,
                ) = Properties()
            }

        val properties =
            manager.getDebeziumProperties(mock(AirbyteFileOffsetBackingStore::class.java))

        assertEquals("8", properties.getProperty("max.queue.size"))
        assertEquals("8", properties.getProperty("max.batch.size"))
    }
}
