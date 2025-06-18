/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper.getIpAddress
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper.getPassword
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper.getPort
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseContainerHelper.getUsername

class ClickhouseConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        var updatedConfig = config

        updatedConfig =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                getPort()?.let { updatedConfig.replace("8123", it.toString()) } ?: updatedConfig
            } else {
                getIpAddress()?.let { updatedConfig.replace("localhost", it) } ?: updatedConfig
            }

        updatedConfig = updatedConfig.replace("replace_me_username", getUsername())
        updatedConfig = updatedConfig.replace("replace_me_password", getPassword())

        return updatedConfig
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(updatedConfig = config, actualDefaultNamespace = defaultNamespace)
}
