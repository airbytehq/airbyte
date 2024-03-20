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
        Assertions.assertThrows(IllegalStateException::class.java) { DestinationConfig.instance }

        // good initialization
        DestinationConfig.initialize(NODE, true)
        Assertions.assertNotNull(DestinationConfig.instance)
        Assertions.assertEquals(NODE, DestinationConfig.instance!!.root)
        Assertions.assertEquals(true, DestinationConfig.instance!!.isV2Destination)

        // initializing again doesn't change the config
        val nodeUnused = Jsons.deserialize("{}")
        DestinationConfig.initialize(nodeUnused, false)
        Assertions.assertEquals(NODE, DestinationConfig.instance!!.root)
        Assertions.assertEquals(true, DestinationConfig.instance!!.isV2Destination)
    }

    @Test
    fun testValues() {
        DestinationConfig.clearInstance()
        DestinationConfig.initialize(NODE)

        Assertions.assertEquals("bar", DestinationConfig.instance!!.getTextValue("foo"))
        Assertions.assertEquals("", DestinationConfig.instance!!.getTextValue("baz"))

        Assertions.assertFalse(DestinationConfig.instance!!.getBooleanValue("foo"))
        Assertions.assertTrue(DestinationConfig.instance!!.getBooleanValue("baz"))

        // non-existent key
        Assertions.assertEquals("", DestinationConfig.instance!!.getTextValue("blah"))
        Assertions.assertFalse(DestinationConfig.instance!!.getBooleanValue("blah"))

        Assertions.assertEquals(
            Jsons.deserialize("\"bar\""),
            DestinationConfig.instance!!.getNodeValue("foo")
        )
        Assertions.assertEquals(
            Jsons.deserialize("true"),
            DestinationConfig.instance!!.getNodeValue("baz")
        )
        Assertions.assertNull(DestinationConfig.instance!!.getNodeValue("blah"))

        Assertions.assertEquals(false, DestinationConfig.instance!!.isV2Destination)
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
