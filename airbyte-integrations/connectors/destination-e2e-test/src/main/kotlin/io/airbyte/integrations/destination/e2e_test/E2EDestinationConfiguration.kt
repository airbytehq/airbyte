/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import io.airbyte.cdk.command.DefaultWriteConfiguration
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class E2EDestinationConfiguration(
    val testDestination: TestDestination,
    override val recordBatchSizeBytes: Long
) : DefaultWriteConfiguration(), DestinationConfiguration

@Factory
class E2EDestinationConfigurationFactory :
    DestinationConfigurationFactory<
        E2EDestinationConfigurationJsonObject, E2EDestinationConfiguration> {

    @Singleton
    override fun makeWithoutExceptionHandling(
        pojo: E2EDestinationConfigurationJsonObject
    ): E2EDestinationConfiguration {
        return E2EDestinationConfiguration(pojo.testDestination, pojo.recordBatchSizeBytes)
    }
}
