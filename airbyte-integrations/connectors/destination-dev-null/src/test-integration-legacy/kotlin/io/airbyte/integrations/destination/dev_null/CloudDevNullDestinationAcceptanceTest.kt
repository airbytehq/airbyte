/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class CloudDevNullDestinationAcceptanceTest : TestingSilentDestinationAcceptanceTest() {
    override val isCloudTest = true

    override fun getConfig(): JsonNode {
        return Jsons.readTree("""{"test_destination": {"test_destination_type": "SILENT"}}""")
    }

    override fun getFailCheckConfig(): JsonNode {
        return Jsons.readTree("""{"test_destination": {"test_destination_type": "invalid"}}""")
    }

    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return emptyList()
    }

    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        // do nothing
    }

    override fun tearDown(testEnv: TestDestinationEnv) {
        // do nothing
    }

    override fun assertSameMessages(
        expected: List<AirbyteMessage>,
        actual: List<AirbyteRecordMessage>,
        pruneAirbyteInternalFields: Boolean
    ) {
        Assertions.assertEquals(0, actual.size)
    }

    // Skip because `retrieveRecords` returns an empty list at all times.
    @Disabled @Test override fun testSyncNotFailsWithNewFields() {}

    @Disabled @Test override fun testAirbyteTimeTypes() {}

    open override fun getDefaultSchema(config: JsonNode): String? {
        return super.getDefaultSchema(config) ?: "default_schema"
    }
}
