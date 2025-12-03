/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getHost
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getIpAddress
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getPassword
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getPort
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getUsername
import io.airbyte.integrations.destination.mysql.MySQLContainerHelper.getDatabase

class MySQLConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        // Ensure container is started before getting connection details
        MySQLContainerHelper.start()

        var updatedConfig = config

        updatedConfig =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                getPort()?.let { updatedConfig.replace("3306", it.toString()) } ?: updatedConfig
            } else {
                getIpAddress()?.let { updatedConfig.replace("localhost", it) } ?: updatedConfig
            }

        updatedConfig = updatedConfig.replace("replace_me_username", getUsername())
        updatedConfig = updatedConfig.replace("replace_me_password", getPassword())
        updatedConfig = updatedConfig.replace("replace_me_database", getDatabase())

        return updatedConfig
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            // Replace only the database name, not other occurrences
            updatedConfig = config.replace(MySQLContainerHelper.DATABASE_NAME, defaultNamespace),
            actualDefaultNamespace = defaultNamespace
        )
}
