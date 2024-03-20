/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
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
    internal fun testRetrievingTheRawNamespaceFromTheConfiguration() {
        val namespace = "test"
        val configuration = TestConnectorConfiguration(namespace)
        assertEquals(namespace, configuration.getRawNamespace().get())

        val configuration2 = TestConnectorConfiguration(null)
        assertFalse(configuration2.getRawNamespace().isPresent)
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

@JsonIgnoreProperties("rawNamespace")
class TestConnectorConfiguration(val namespace: String?) : ConnectorConfiguration {
    override fun getDefaultNamespace(): Optional<String> {
        return Optional.ofNullable(namespace)
    }

    override fun getRawNamespace(): Optional<String> {
        return Optional.ofNullable(namespace)
    }
}
