/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component.config

import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class ComponentTestConfigFactory {
    @Singleton
    @Primary
    fun config(): ClickhouseConfiguration {
        return loadTestConfig(
            ClickhouseSpecificationOss::class.java,
            ClickhouseConfigurationFactory::class.java,
            "test-instance.json",
        )
    }
}
