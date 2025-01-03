/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.MSSQLServerContainer

val logger = KotlinLogging.logger {}

/**
 * Helper class for launching/stopping MSSQL Server test containers, as well as updating destination
 * configuration to match test container configuration.
 */
object MSSQLContainerHelper : ConfigurationUpdater {

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
    override fun update(config: String): String {
        return getHost()?.let { host ->
            config.replace("localhost", host).replace("replace_me", testContainer.password)
        }
            ?: config
    }
    private fun getHost(): String? {
        // Ensure that the container is started first
        start()
        return testContainer.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }
}
