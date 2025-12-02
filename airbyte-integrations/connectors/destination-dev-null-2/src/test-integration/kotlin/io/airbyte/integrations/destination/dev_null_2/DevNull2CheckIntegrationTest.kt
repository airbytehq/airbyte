/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import org.junit.jupiter.api.Test

class DevNull2CheckIntegrationTest :
    CheckIntegrationTest<DevNull2SpecificationOss>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(DevNull2TestUtils.configContents()),
            ),
        failConfigFilenamesAndFailureReasons = mapOf(),
    ) {

    @Test
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
