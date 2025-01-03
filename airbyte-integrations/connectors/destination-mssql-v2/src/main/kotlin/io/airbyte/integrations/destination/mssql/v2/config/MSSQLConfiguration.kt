/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import dagger.Component.Factory
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class MSSQLConfiguration(val placeholder: String) : DestinationConfiguration()

@Singleton
class MSSQLConfigurationFactory :
    DestinationConfigurationFactory<MSSQLSpecification, MSSQLConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: MSSQLSpecification): MSSQLConfiguration {
        TODO("Not yet implemented")
    }
}

@Factory
class MSSQLConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): MSSQLConfiguration {
        return config as MSSQLConfiguration
    }
}
