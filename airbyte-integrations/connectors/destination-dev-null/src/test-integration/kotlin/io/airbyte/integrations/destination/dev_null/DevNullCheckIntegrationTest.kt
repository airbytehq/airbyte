/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.test.util.destination_process.TestDeploymentMode
import java.util.regex.Pattern
import org.junit.jupiter.api.Test

class DevNullCheckIntegrationTest :
    CheckIntegrationTest<DevNullSpecificationOss>(
        DevNullSpecificationOss::class.java,
        successConfigFilenames =
            listOf(
                CheckTestConfig(DevNullTestUtils.LOGGING_CONFIG_PATH, TestDeploymentMode.OSS),
            ),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                // cloud doesn't support logging mode, so this should fail
                // when trying to parse the config
                CheckTestConfig(DevNullTestUtils.LOGGING_CONFIG_PATH, TestDeploymentMode.CLOUD) to
                    Pattern.compile("Value 'LOGGING' is not defined in the schema")
            ),
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
