/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class SnowflakeBeansFactory {
    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun snowflakeConfiguration(
        configFactory: SnowflakeConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<SnowflakeSpecification>,
    ): SnowflakeConfiguration {
        val spec = specFactory.get()

        return configFactory.makeWithoutExceptionHandling(spec)
    }
}
