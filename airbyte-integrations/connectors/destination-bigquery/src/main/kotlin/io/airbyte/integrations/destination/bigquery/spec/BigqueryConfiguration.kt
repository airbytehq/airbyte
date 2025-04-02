/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

// TODO
data class BigqueryConfiguration(val x: String) : DestinationConfiguration()

@Singleton
class BigqueryConfigurationFactory :
    DestinationConfigurationFactory<BigquerySpecification, BigqueryConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: BigquerySpecification): BigqueryConfiguration {
        return BigqueryConfiguration("arst")
    }
}

@Factory
class BigqueryConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton fun get() = config as BigqueryConfiguration
}
