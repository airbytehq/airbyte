/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.container

import org.testcontainers.containers.MSSQLServerContainer

object MSSQLContainer {

    private val testContainer = MSSQLServerContainer("mcr.microsoft.com/mssql/server:2022-latest")
        .acceptLicense()
        .withPassword("Averycomplicatedpassword1!")

    val hostConfigUpdater = { config: String ->
        getHost()?.let { host ->
            config.replace("localhost", host)
        } ?: config
    }

    fun start() {
        if (!testContainer.isRunning()) {
            testContainer.start()
        }
    }

    fun getHost(): String? {
        // Ensure that the container is started first
        start()
        return testContainer.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }

    fun stop() {
        if (testContainer.isRunning()) {
            testContainer.stop()
        }
    }
}
