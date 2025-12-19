/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component.config

import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class SnowflakeTestConfigFactory {
    @Singleton
    @Primary
    fun config(): SnowflakeConfiguration {
        return loadTestConfig(
            SnowflakeSpecification::class.java,
            SnowflakeConfigurationFactory::class.java,
            "config_with_auth_staging.json",
        )
    }
}
