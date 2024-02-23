/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test
import java.util.Optional

class ConnectorConfigurationTest {
    @Test
    internal fun `test retrieving the raw namespace from the configuration`() {
        val namespace = "test"
        val configuration = TestConnectorConfiguration(namespace)
        assertEquals(namespace, configuration.getRawNamespace().get())

        val configuration2 = TestConnectorConfiguration(null)
        assertFalse(configuration2.getRawNamespace().isPresent)
    }

    @Test
    internal fun `test converting the configuration to JSON`() {
        val namespace = "test"
        val configuration = TestConnectorConfiguration(namespace)
        val json = configuration.toJson()
        assertNotNull(json)
        assertEquals(namespace, json.get("namespace").textValue())
    }
}

@JsonIgnoreProperties("rawNamespace")
class TestConnectorConfiguration(val namespace: String?) : ConnectorConfiguration {
    override fun getRawNamespace(): Optional<String> {
        return Optional.ofNullable(namespace)
    }
}
