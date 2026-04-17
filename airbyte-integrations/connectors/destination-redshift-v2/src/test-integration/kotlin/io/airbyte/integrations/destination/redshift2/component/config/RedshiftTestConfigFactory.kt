/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.component.config

import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class RedshiftTestConfigFactory {
    @Singleton
    @Primary
    fun config(): RedshiftConfiguration {
        return loadTestConfig(
            RedshiftSpecification::class.java,
            RedshiftConfigurationFactory::class.java,
            "config_staging.json",
        )
    }

    /**
     * Explicit bean to avoid Micronaut trying to inject Kotlin default constructor args
     * (Int/String) as beans, which causes NPE at runtime.
     */
    @Singleton
    @Primary
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()
}
