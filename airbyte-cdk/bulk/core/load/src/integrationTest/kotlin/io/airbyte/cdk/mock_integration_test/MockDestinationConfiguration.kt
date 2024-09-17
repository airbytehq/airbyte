/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.mock_integration_test

import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

class MockDestinationConfiguration : DestinationConfiguration()

@Singleton class MockDestinationSpecification : ConfigurationJsonObjectBase()

@Singleton
class MockDestinationConfigurationFactory :
    DestinationConfigurationFactory<MockDestinationSpecification, MockDestinationConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MockDestinationSpecification
    ): MockDestinationConfiguration {
        return MockDestinationConfiguration()
    }
}

@Factory
class MockDestinationConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): MockDestinationConfiguration {
        return config as MockDestinationConfiguration
    }
}
