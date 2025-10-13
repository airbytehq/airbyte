/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component.config

import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.nio.file.Files
import kotlin.io.path.Path

@Factory
class TestConfigBeanOverrides {
    @Singleton
    @Primary
    fun config(): ClickhouseConfiguration {
        val configPath = Path("secrets/test-instance.json")
        val configStr = Files.readString(configPath)
        val spec = Jsons.readValue(configStr, ClickhouseSpecificationOss::class.java)

        return ClickhouseConfigurationFactory().makeWithoutExceptionHandling(spec)
    }
}
