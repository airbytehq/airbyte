/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DestinationConfigTest {
    @Test
    fun testInitialization() {
        // bad initialization
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            DestinationConfig.initialize(null)
        }
        Assertions.assertThrows(IllegalStateException::class.java) {
            DestinationConfig.getInstance()
        }

        // good initialization
        DestinationConfig.initialize(NODE, true)
        Assertions.assertNotNull(DestinationConfig.getInstance())
        Assertions.assertEquals(NODE, DestinationConfig.getInstance().root)
        Assertions.assertEquals(true, DestinationConfig.getInstance().isV2Destination)

        // initializing again doesn't change the config
        val nodeUnused = Jsons.deserialize("{}")
        DestinationConfig.initialize(nodeUnused, false)
        Assertions.assertEquals(NODE, DestinationConfig.getInstance().root)
        Assertions.assertEquals(true, DestinationConfig.getInstance().isV2Destination)
    }

    @Test
    fun testValues() {
        DestinationConfig.clearInstance()
        DestinationConfig.initialize(NODE)

        Assertions.assertEquals("bar", DestinationConfig.getInstance().getTextValue("foo"))
        Assertions.assertEquals("", DestinationConfig.getInstance().getTextValue("baz"))

        Assertions.assertFalse(DestinationConfig.getInstance().getBooleanValue("foo"))
        Assertions.assertTrue(DestinationConfig.getInstance().getBooleanValue("baz"))

        // non-existent key
        Assertions.assertEquals("", DestinationConfig.getInstance().getTextValue("blah"))
        Assertions.assertFalse(DestinationConfig.getInstance().getBooleanValue("blah"))

        Assertions.assertEquals(
            Jsons.deserialize("\"bar\""),
            DestinationConfig.getInstance().getNodeValue("foo")
        )
        Assertions.assertEquals(
            Jsons.deserialize("true"),
            DestinationConfig.getInstance().getNodeValue("baz")
        )
        Assertions.assertNull(DestinationConfig.getInstance().getNodeValue("blah"))

        Assertions.assertEquals(false, DestinationConfig.getInstance().isV2Destination)
    }

    companion object {
        private val JSON =
            """
                                     {
                                       "foo": "bar",
                                       "baz": true
                                     }
                                     
                                     """.trimIndent()

        private val NODE: JsonNode = Jsons.deserialize(JSON)
    }
}
