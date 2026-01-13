/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.mock

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

data class MockDestinationConfiguration(val foo: Int) : DestinationConfiguration() {
    // Micro-batch for testing.
    override val recordBatchSizeBytes = 1L
}

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationSpecification : ConfigurationSpecification() {
    val foo: Int = 0

    companion object {
        const val CONFIG: String = """{"foo": 0}"""
        const val BAD_CONFIG: String = """{"foo": 1}"""
    }
}

@Singleton
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationConfigurationFactory :
    DestinationConfigurationFactory<MockDestinationSpecification, MockDestinationConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MockDestinationSpecification
    ): MockDestinationConfiguration {
        return MockDestinationConfiguration(foo = pojo.foo)
    }
}

@Factory
@Requires(env = [MOCK_TEST_MICRONAUT_ENVIRONMENT])
class MockDestinationConfigurationProvider {
    @Singleton
    fun get(config: DestinationConfiguration): MockDestinationConfiguration {
        return config as MockDestinationConfiguration
    }
}
