/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class AirbyteConnectorStateTest {
    @Test
    internal fun testThatANonEmptyConnectorStateCanBeConvertedToJSON() {
        val connectorState = AirbyteConnectorState()
        connectorState.json = "{\"cursor\":\"foo\"}"
        val stateJson = connectorState.toJson()
        assertNotNull(stateJson)
        assertEquals(connectorState.json, Jsons.serialize(stateJson))
    }

    @Test
    internal fun testThatAnEmptyConnectorStateResultsInEmptyJSON() {
        val connectorState = AirbyteConnectorState()
        connectorState.json = ""
        val stateJson = connectorState.toJson()
        assertNotNull(stateJson)
        assertTrue(stateJson.isEmpty)
    }
}
