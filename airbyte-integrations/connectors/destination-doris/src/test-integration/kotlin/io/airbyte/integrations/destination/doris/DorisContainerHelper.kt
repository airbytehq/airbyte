/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris

import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.DriverManager
import java.time.Duration
import java.util.concurrent.locks.LockSupport
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.Network
import org.testcontainers.containers.output.Slf4jLogConsumer
import org.testcontainers.utility.DockerLoggerFactory
import org.testcontainers.utility.MountableFile

private val log = KotlinLogging.logger {}

/**
 * Manages a Doris all-in-one Docker container for integration testing. Based on the Flink Doris
 * Connector's DorisContainer.java.
 */
object DorisContainerHelper {

    private const val DOCKER_IMAGE = "apache/doris:doris-all-in-one-2.1.0"
    private const val JDBC_URL_TEMPLATE = "jdbc:mysql://%s:%d"
    private const val USERNAME = "root"
    private const val PASSWORD = ""

    const val HTTP_PORT = 8030
    const val QUERY_PORT = 9030
    private const val BE_WEBSERVER_PORT = 8040
    private const val BE_ADMIN_PORT = 9060

    private val container: GenericContainer<*> =
        GenericContainer(DOCKER_IMAGE)
            .withNetwork(Network.newNetwork())
            .withNetworkAliases("DorisContainer")
            .withPrivilegedMode(true)
            .withLogConsumer(Slf4jLogConsumer(DockerLoggerFactory.getLogger(DOCKER_IMAGE)))
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("docker/doris/be.conf"),
                "/opt/apache-doris/be/conf/be.conf"
            )
            .withCopyFileToContainer(
                MountableFile.forClasspathResource("docker/doris/fe.conf"),
                "/opt/apache-doris/fe/conf/fe.conf"
            )
            .withExposedPorts(HTTP_PORT, QUERY_PORT, BE_WEBSERVER_PORT, BE_ADMIN_PORT)

    init {
        container.setPortBindings(
            listOf(
                "$HTTP_PORT:$HTTP_PORT",
                "$QUERY_PORT:$QUERY_PORT",
                "$BE_WEBSERVER_PORT:$BE_WEBSERVER_PORT",
                "$BE_ADMIN_PORT:$BE_ADMIN_PORT",
            )
        )
    }

    fun start() {
        synchronized(container) {
            if (!container.isRunning) {
                log.info { "Starting Doris container..." }
                container.start()
                waitForBackendReady()
                log.info { "Doris container started successfully." }
            }
        }
    }

    fun stop() {
        synchronized(container) {
            if (container.isRunning) {
                container.stop()
                log.info { "Doris container stopped." }
            }
        }
    }

    fun getHost(): String = container.host

    fun getHttpPort(): Int = container.getMappedPort(HTTP_PORT)

    fun getQueryPort(): Int = container.getMappedPort(QUERY_PORT)

    fun getUsername(): String = USERNAME

    fun getPassword(): String = PASSWORD

    fun getJdbcUrl(): String = String.format(JDBC_URL_TEMPLATE, getHost(), getQueryPort())

    fun getConnection(): Connection {
        Class.forName("com.mysql.cj.jdbc.Driver")
        val conn = DriverManager.getConnection(getJdbcUrl(), USERNAME, PASSWORD)
        conn.createStatement().use { it.execute("SET time_zone = '+00:00'") }
        return conn
    }

    fun getConnection(database: String): Connection {
        Class.forName("com.mysql.cj.jdbc.Driver")
        val conn = DriverManager.getConnection("${getJdbcUrl()}/$database", USERNAME, PASSWORD)
        conn.createStatement().use { it.execute("SET time_zone = '+00:00'") }
        return conn
    }

    /**
     * Wait for the Backend node to be alive and have capacity. This is the same approach used by
     * the Flink Doris Connector.
     */
    private fun waitForBackendReady() {
        log.info { "Waiting for Doris Backend to be ready..." }
        val maxWaitMs = 120_000L
        val startTime = System.currentTimeMillis()

        while (System.currentTimeMillis() - startTime < maxWaitMs) {
            try {
                getConnection().use { conn ->
                    conn.createStatement().use { stmt ->
                        val rs = stmt.executeQuery("SHOW BACKENDS")
                        if (rs.next()) {
                            val alive = rs.getString("Alive").trim()
                            val totalCapacity = rs.getString("TotalCapacity").trim()
                            if (
                                alive.equals("true", ignoreCase = true) && totalCapacity != "0.000"
                            ) {
                                log.info {
                                    "Doris Backend is ready. Alive=$alive, TotalCapacity=$totalCapacity"
                                }
                                return
                            }
                        }
                    }
                }
            } catch (_: Exception) {
                // Connection not ready yet
            }
            LockSupport.parkNanos(Duration.ofSeconds(2).toNanos())
        }
        throw RuntimeException(
            "Doris Backend did not become ready within ${maxWaitMs / 1000} seconds"
        )
    }
}
