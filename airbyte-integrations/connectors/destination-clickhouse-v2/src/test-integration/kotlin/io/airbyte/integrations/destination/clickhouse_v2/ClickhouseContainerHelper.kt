/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2

import org.testcontainers.clickhouse.ClickHouseContainer

object ClickhouseContainerHelper {
    private val container = ClickHouseContainer("clickhouse/clickhouse-server:latest")

    fun start() {
        synchronized(lock = container) {
            if (!container.isRunning()) {
                container.start()
            }
        }
    }

    /** This method cleanly stop the test container if it is running. */
    fun stop() {
        synchronized(lock = container) {
            if (container.isRunning()) {
                container.stop()
            }
        }
    }

    fun getPassword(): String = container.password

    fun getPort(): Int? = container.getMappedPort(8123)

    fun getUsername(): String = container.username

    fun getIpAddress(): String? {
        // Ensure that the container is started first
        start()
        return container.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }
}
