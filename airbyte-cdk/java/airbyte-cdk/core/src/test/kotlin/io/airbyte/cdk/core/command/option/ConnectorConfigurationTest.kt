/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

class ConnectorConfigurationTest {
    @Test
    internal fun testRetrievingTheDefaultNamespaceFromTheConfiguration() {
        val namespace = "test"
        val configuration = TestConnectorConfiguration(namespace)
        assertEquals(namespace, configuration.getDefaultNamespace().get())

        val configuration2 = TestConnectorConfiguration(null)
        assertFalse(configuration2.getDefaultNamespace().isPresent)
    }

    @Test
    internal fun testConvertingTheConfigurationToJSON() {
        val namespace = "test"
        val configuration = TestConnectorConfiguration(namespace)
        val json = configuration.toJson()
        assertNotNull(json)
        assertEquals(namespace, json.get("namespace").textValue())
    }
}

class TestConnectorConfiguration(val namespace: String?) : ConnectorConfiguration {
    override fun getDefaultNamespace(): Optional<String> {
        return Optional.ofNullable(namespace)
    }
}
