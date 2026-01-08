/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import java.util.regex.Pattern
import org.junit.jupiter.api.Test

class DevNullV2CheckTest :
    CheckIntegrationTest<DevNullV2Specification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig("""{"test_destination": {"test_destination_type": "SILENT"}}"""),
                CheckTestConfig(
                    """{"test_destination": {"test_destination_type": "LOGGING", "logging_config": {"logging_type": "FirstN", "max_entry_count": 100}}}"""
                )
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig("""{"test_destination": {"test_destination_type": "INVALID"}}""") to
                    Pattern.compile(".*"),
                CheckTestConfig(
                    """{"test_destination": {"test_destination_type": "LOGGING", "logging_config": {"logging_type": "EveryNth", "nth_entry_to_log": -1, "max_entry_count": 100}}}"""
                ) to Pattern.compile(".*must be positive.*")
            )
    ) {

    @Test
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }

    @Test
    override fun testFailConfigs() {
        super.testFailConfigs()
    }
}
