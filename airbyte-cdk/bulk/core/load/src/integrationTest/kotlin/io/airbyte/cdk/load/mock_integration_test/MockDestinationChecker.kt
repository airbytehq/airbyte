/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.mock_integration_test.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.micronaut.context.annotation.Requires
import javax.inject.Singleton

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationChecker : DestinationChecker<MockDestinationConfiguration> {
    override fun check(config: MockDestinationConfiguration) {}
}
