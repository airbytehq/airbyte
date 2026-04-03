/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import org.testcontainers.containers.MySQLContainer

object MySQLContainerHelper {
    // Use a unique database name that won't conflict with password in string replacement
    const val DATABASE_NAME = "airbyte_test_db"
    const val PASSWORD = "testpassword"

    private val container = MySQLContainer("mysql:8.0")
        .withDatabaseName(DATABASE_NAME)
        .withUsername("root")
        .withPassword(PASSWORD)
        .withEnv("MYSQL_ROOT_PASSWORD", PASSWORD)
        .withCommand(
            "--character-set-server=utf8mb4",
            "--collation-server=utf8mb4_unicode_ci",
            "--max_connections=500"
        )

    fun start() {
        synchronized(lock = container) {
            if (!container.isRunning) {
                container.start()
            }
        }
    }

    fun stop() {
        synchronized(lock = container) {
            if (container.isRunning) {
                container.stop()
            }
        }
    }

    fun getPassword(): String = PASSWORD

    fun getPort(): Int? = container.getMappedPort(3306)

    fun getUsername(): String = "root"

    fun getDatabase(): String = container.databaseName

    fun getHost(): String = container.host

    fun getIpAddress(): String? {
        start()
        return container.containerInfo.networkSettings.networks.entries.first().value.ipAddress
    }
}
