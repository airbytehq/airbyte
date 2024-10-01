/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.test.check.CheckIntegrationTest
import org.junit.jupiter.api.Test

class DevNullCheckIntegrationTest :
    CheckIntegrationTest<DevNullSpecificationOss>(
        DevNullSpecificationOss::class.java,
        successConfigFilenames = listOf(DevNullTestUtils.LOGGING_CONFIG_PATH),
        failConfigFilenamesAndFailureReasons = mapOf(),
    ) {

    @Test
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }
}
