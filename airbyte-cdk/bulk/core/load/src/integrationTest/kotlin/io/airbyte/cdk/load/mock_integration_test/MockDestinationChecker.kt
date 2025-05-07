/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.check.DestinationChecker
import javax.inject.Singleton

@Singleton
class MockDestinationChecker : DestinationChecker<MockDestinationConfiguration> {
    override fun check(config: MockDestinationConfiguration) {
        if (config.foo != 0) {
            throw IllegalArgumentException("Foo should be 0")
        }
    }
}
