/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceDebeziumOperations
import io.airbyte.integrations.source.postgres.cdc.ReplicationSlotManager
import io.airbyte.integrations.source.postgres.cdc.StartupState
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.mockk.every
import io.mockk.mockk
import java.net.InetSocketAddress
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Verifies that [PostgresSourceDebeziumOperations] passes the SSH tunnel's local forwarded address
 * to Debezium, not the raw remote host/port from the configuration.
 *
 * This is a regression test for the bug where Debezium would try to connect directly to the remote
 * database host, bypassing the SSH tunnel entirely.
 */
class PostgresSourceDebeziumOperationsSshTunnelTest {

    @Test
    fun `commonPropertiesBuilder uses tunnel session address instead of raw config host`() {
        val remoteHost = "remote-db.internal.example.com"
        val remotePort = 5432
        val tunnelLocalHost = "127.0.0.1"
        val tunnelLocalPort = 54321

        val tunnelSession =
            mockk<TunnelSession> {
                every { address } returns
                    InetSocketAddress.createUnresolved(tunnelLocalHost, tunnelLocalPort)
            }

        val connectionFactory =
            mockk<PostgresSourceJdbcConnectionFactory> {
                every { ensureTunnelSession() } returns tunnelSession
            }

        val cdcConfig =
            CdcIncrementalConfiguration(
                initialLoadTimeout = Duration.ofHours(8),
                invalidCdcCursorPositionBehavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                shutdownTimeout = Duration.ofSeconds(60),
                replicationSlot = "test_slot",
                publication = "test_publication",
                debeziumCommitsLsn = false,
                heartbeatActionQuery = null,
                airbyteHeartbeatTimeout = Duration.ofSeconds(1200),
            )

        val config =
            PostgresSourceConfiguration(
                realHost = remoteHost,
                realPort = remotePort,
                sshTunnel =
                    SshKeyAuthTunnelMethod(
                        host = "bastion.example.com",
                        port = 22,
                        user = "sshuser",
                        key = "fake-key",
                    ),
                sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
                jdbcUrlFmt = "jdbc:postgresql://%s:%d/testdb",
                jdbcProperties =
                    mapOf(
                        "user" to "testuser",
                        "password" to "testpass",
                    ),
                database = "testdb",
                namespaces = setOf("public"),
                incrementalConfiguration = cdcConfig,
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(60),
                checkPrivileges = true,
            )

        val replicationSlotManager = mockk<ReplicationSlotManager>(relaxed = true)
        val startupState = mockk<StartupState>(relaxed = true)

        val ops =
            PostgresSourceDebeziumOperations(
                config = config,
                connectionFactory = connectionFactory,
                replicationSlotManager = replicationSlotManager,
                startupState = startupState,
            )

        // Access the lazy commonPropertiesBuilder, which triggers ensureTunnelSession()
        // and builds the Debezium properties map.
        val props = ops.commonPropertiesBuilder

        // Extract the built properties by calling buildMap with a dummy stream list.
        // We use reflection-free approach: the builder has withDatabase("hostname", ...) and
        // withDatabase("port", ...) which set "database.hostname" and "database.port".
        // We can inspect these by building the map (needs streams, but we can check the builder).
        // Instead, let's use the generateColdStartProperties or generateWarmStartProperties
        // which call commonPropertiesBuilder.withStreams(streams).buildMap().
        // For simplicity, build with empty streams list.
        val propsMap = props.withStreams(emptyList()).buildMap()

        assertEquals(
            tunnelLocalHost,
            propsMap["database.hostname"],
            "Debezium should connect to the SSH tunnel's local address, not the remote host",
        )
        assertEquals(
            tunnelLocalPort.toString(),
            propsMap["database.port"],
            "Debezium should connect to the SSH tunnel's local port, not the remote port",
        )
    }
}
