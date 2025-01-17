/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getIpAddress
import io.airbyte.integrations.destination.mssql.v2.MSSQLContainerHelper.getPort
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.MSSQLServerContainer
import org.testcontainers.containers.MSSQLServerContainer.MS_SQL_SERVER_PORT

val logger = KotlinLogging.logger {}

/**
 * Helper class for launching/stopping MSSQL Server test containers, as well as updating destination
 * configuration to match test container configuration.
 */
object MSSQLContainerHelper {

    private val testContainer =
        MSSQLServerContainer("mcr.microsoft.com/mssql/server:2022-latest")
            .acceptLicense()
            .withLogConsumer({ e -> logger.debug { e.utf8String } })

    fun start() {
        if (!testContainer.isRunning()) {
            testContainer.start()
        }
    }
    fun stop() {
        if (testContainer.isRunning()) {
            testContainer.stop()
            testContainer.close()
        }
    }

    fun getHost(): String = testContainer.host

    fun getPassword(): String = testContainer.password

    fun getPort(): Int? = testContainer.getMappedPort(MS_SQL_SERVER_PORT)

    fun getIpAddress(): String? {
        // Ensure that the container is started first
        start()
        return testContainer.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }
}

class MSSQLConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        var updatedConfig = getIpAddress()?.let { config.replace("localhost", it) } ?: config

        // If not running the connector in docker, we must use the mapped port to connect to the
        // database.
        if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
            updatedConfig =
                getPort()?.let { updatedConfig.replace("$MS_SQL_SERVER_PORT", it.toString()) }
                    ?: updatedConfig
        }

        updatedConfig = updatedConfig.replace("replace_me", MSSQLContainerHelper.getPassword())
        logger.debug { "Using updated MSSQL configuration: $updatedConfig" }
        return updatedConfig
    }
}
