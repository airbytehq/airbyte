/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

class AirbyteConfiguredCatalogTest {
    @Test
    internal fun `test that a non-empty configured catalog can be converted`() {
        val streamName = "test-name"
        val streamNamespace = "test-namespace"
        val catalog = AirbyteConfiguredCatalog()
        catalog.json =
            "{\"streams\":[{\"stream\":{\"name\":\"$streamName\",\"namespace\":\"$streamNamespace\"}}]}"
        val configuredCatalog = catalog.getConfiguredCatalog()
        assertNotNull(configuredCatalog)
        assertEquals(1, configuredCatalog.streams.size)
        assertEquals(streamName, configuredCatalog.streams.first().stream.name)
        assertEquals(streamNamespace, configuredCatalog.streams.first().stream.namespace)
    }

    @Test
    internal fun `test that an empty configured catalog results in an emtpy configured catalog`() {
        val catalog = AirbyteConfiguredCatalog()
        catalog.json = ""
        val configuredCatalog = catalog.getConfiguredCatalog()
        assertNotNull(configuredCatalog)
        assertEquals(0, configuredCatalog.streams.size)
    }
}
