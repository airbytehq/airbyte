/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

class MockDestinationConfiguration : DestinationConfiguration() {
    // Micro-batch for testing.
    override val recordBatchSizeBytes = 1L
}

@Singleton
class MockDestinationSpecification : ConfigurationSpecification() {
    companion object {
        const val CONFIG: String = "{}"
    }
}

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
