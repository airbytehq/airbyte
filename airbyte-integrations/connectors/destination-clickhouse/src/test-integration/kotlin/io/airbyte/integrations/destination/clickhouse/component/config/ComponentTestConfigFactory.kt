/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component.config

import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.clickhouse.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse.ClickhouseContainerHelper
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
        ClickhouseContainerHelper.start()

        val configJson =
            """
            {
                "host": "localhost",
                "port": "8123",
                "protocol": "http",
                "username": "replace_me_username",
                "password": "replace_me_password",
                "database": "default",
                "enable_json": true
            }
        """

        val updatedConfig = ClickhouseConfigUpdater().update(configJson)
        val spec = Jsons.readValue(updatedConfig, ClickhouseSpecificationOss::class.java)
        return ClickhouseConfigurationFactory().makeWithoutExceptionHandling(spec)
    }
}
