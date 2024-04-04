/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class AirbyteConnectorStateTest {
    @Test
    internal fun `test that a non-empty connector state can be converted to JSON`() {
        val connectorState = AirbyteConnectorState()
        connectorState.json = "{\"cursor\":\"foo\"}"
        val stateJson = connectorState.toJson()
        assertNotNull(stateJson)
        assertEquals(connectorState.json, Jsons.serialize(stateJson))
    }

    @Test
    internal fun `test that an empty connector state results in empty JSON`() {
        val connectorState = AirbyteConnectorState()
        connectorState.json = ""
        val stateJson = connectorState.toJson()
        assertNotNull(stateJson)
        assertTrue(stateJson.isEmpty)
    }
}
