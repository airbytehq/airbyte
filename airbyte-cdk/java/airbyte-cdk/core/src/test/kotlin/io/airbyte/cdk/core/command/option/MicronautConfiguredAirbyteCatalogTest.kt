/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

class MicronautConfiguredAirbyteCatalogTest {
    @Test
    internal fun testThatANonEmptyConfiguredCatalogCanBeConverted() {
        val streamName = "test-name"
        val streamNamespace = "test-namespace"
        val catalog = MicronautConfiguredAirbyteCatalog()
        catalog.json =
            "{\"streams\":[{\"stream\":{\"name\":\"$streamName\",\"namespace\":\"$streamNamespace\"}}]}"
        val configuredCatalog = catalog.getConfiguredCatalog()
        assertNotNull(configuredCatalog)
        assertEquals(1, configuredCatalog.streams.size)
        assertEquals(streamName, configuredCatalog.streams.first().stream.name)
        assertEquals(streamNamespace, configuredCatalog.streams.first().stream.namespace)
    }

    @Test
    internal fun testThatAnEmptyConfiguredCatalogResultsInAnEmptyConfiguredCatalog() {
        val catalog = MicronautConfiguredAirbyteCatalog()
        catalog.json = ""
        val configuredCatalog = catalog.getConfiguredCatalog()
        assertNotNull(configuredCatalog)
        assertEquals(0, configuredCatalog.streams.size)
    }
}
