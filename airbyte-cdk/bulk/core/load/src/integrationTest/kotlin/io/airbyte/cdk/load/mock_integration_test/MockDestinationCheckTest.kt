/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationSpecification
import java.util.regex.Pattern
import org.junit.jupiter.api.Test

class MockDestinationCheckTest :
    CheckIntegrationTest<MockDestinationSpecification>(
        successConfigFilenames = listOf(CheckTestConfig(MockDestinationSpecification.CONFIG)),
        failConfigFilenamesAndFailureReasons =
            mapOf(
                CheckTestConfig(MockDestinationSpecification.BAD_CONFIG) to
                    Pattern.compile("Foo should be 0")
            ),
        additionalMicronautEnvs = listOf(MOCK_TEST_MICRONAUT_ENVIRONMENT),
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
