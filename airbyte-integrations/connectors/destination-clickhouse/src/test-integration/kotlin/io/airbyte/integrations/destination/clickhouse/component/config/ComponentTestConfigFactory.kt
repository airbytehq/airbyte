/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component.config

import io.airbyte.integrations.destination.clickhouse.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConnectionProtocol
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecification
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
        val isDockerTestRunner = System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") == "docker"
        return ClickhouseConfiguration(
            hostname =
                if (isDockerTestRunner) {
                    ClickhouseContainerHelper.getIpAddress() ?: "localhost"
                } else {
                    "localhost"
                },
            port = if (isDockerTestRunner) "8123" else ClickhouseContainerHelper.getPort().toString(),
            protocol = ClickhouseConnectionProtocol.HTTP.value,
            database = testSpec().database,
            username = ClickhouseContainerHelper.getUsername(),
            password = ClickhouseContainerHelper.getPassword(),
            enableJson = testSpec().enableJson ?: false,
            tunnelConfig = testSpec().getTunnelMethodValue()!!,
            recordWindowSize = testSpec().recordWindowSize,
        )
    }

    private fun testSpec(): ClickhouseSpecification = ClickhouseSpecificationOss()
}
