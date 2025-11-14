/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.PostgreSQLContainer

private val logger = KotlinLogging.logger {}

/**
 * Helper class for launching/stopping PostgreSQL test containers, as well as updating destination
 * configuration to match test container configuration.
 */
object PostgresContainerHelper {

    private val testContainer: PostgreSQLContainer<Nothing> =
        PostgreSQLContainer<Nothing>("postgres:16-alpine").apply {
            withDatabaseName("postgres")
            withUsername("postgres")
            withPassword("postgres")
        }

    fun start() {
        synchronized(lock = testContainer) {
            if (!testContainer.isRunning) {
                testContainer.start()
            }
        }
    }

    /** This method cleanly stops the test container if it is running. */
    fun stop() {
        synchronized(lock = testContainer) {
            if (testContainer.isRunning) {
                testContainer.stop()
            }
        }
    }

    fun getHost(): String = testContainer.host

    fun getPassword(): String = testContainer.password

    fun getPort(): Int = testContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)

    fun getUsername(): String = testContainer.username

    fun getDatabaseName(): String = testContainer.databaseName

    fun getIpAddress(): String {
        // Ensure that the container is started first
        start()
        return testContainer.containerInfo.networkSettings.networks.entries
            .first()
            .value
            .ipAddress!!
    }
}

/**
 * Configuration updater that replaces placeholder values with actual test container connection
 * details.
 */
class PostgresConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String {
        // Ensure the container is started before accessing its configuration
        PostgresContainerHelper.start()

        var updatedConfig = config

        // If not running the connector in docker, we must use the mapped port to connect to the
        // database. Otherwise, get the container's IP address for the host
        updatedConfig =
            if (System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER") != "docker") {
                updatedConfig
                    .replace("replace_me_host", PostgresContainerHelper.getHost())
                    .replace("replace_me_port", PostgresContainerHelper.getPort().toString())
            } else {
                updatedConfig
                    .replace("replace_me_host", PostgresContainerHelper.getIpAddress())
                    .replace("replace_me_port", PostgreSQLContainer.POSTGRESQL_PORT.toString())
            }

        updatedConfig =
            updatedConfig
                .replace("replace_me_database", PostgresContainerHelper.getDatabaseName())
                .replace("replace_me_username", PostgresContainerHelper.getUsername())
                .replace("replace_me_password", PostgresContainerHelper.getPassword())

        logger.debug { "Using updated PostgreSQL configuration: $updatedConfig" }
        return updatedConfig
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(config.replace("public", defaultNamespace), defaultNamespace)
}
