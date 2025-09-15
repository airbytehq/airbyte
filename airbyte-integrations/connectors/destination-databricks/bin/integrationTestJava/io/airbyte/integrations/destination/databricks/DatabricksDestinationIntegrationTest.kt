/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DatabricksDestinationIntegrationTest {

    /** Very basic test that [DatabricksDestination.check] succeeds on a valid config. */
    @Test
    fun testCheckOauthConfig() {
        val config = DatabricksIntegrationTestUtils.oauthConfigJson
        val checkResult = DatabricksDestination().check(config)
        assertEquals(
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
            checkResult,
        )
    }
}
