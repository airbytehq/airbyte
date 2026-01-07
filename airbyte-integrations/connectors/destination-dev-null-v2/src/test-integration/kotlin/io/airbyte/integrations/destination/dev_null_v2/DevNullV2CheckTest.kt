/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import org.junit.jupiter.api.Test
import java.util.regex.Pattern

class DevNullV2CheckTest : CheckIntegrationTest<DevNullV2Specification>(
    successConfigFilenames = listOf(
        CheckTestConfig("""{"mode": "silent", "log_every_n": 1000}"""),
        CheckTestConfig("""{"mode": "logging", "log_every_n": 1}""")
    ),
    failConfigFilenamesAndFailureReasons = mapOf(
        CheckTestConfig("""{"mode": "invalid_mode", "log_every_n": 1000}""") to
            Pattern.compile("Invalid mode: invalid_mode"),
        CheckTestConfig("""{"mode": "silent", "log_every_n": -1}""") to
            Pattern.compile("logEveryN must be positive")
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