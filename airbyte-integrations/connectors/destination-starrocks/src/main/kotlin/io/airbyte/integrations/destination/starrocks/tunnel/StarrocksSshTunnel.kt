/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.tunnel

import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.sshd.common.util.net.SshdSocketAddress

private val log = KotlinLogging.logger {}

/**
 * Optional SSH tunnel (issue #68) for the **JDBC control plane only**. A configured jump server is
 * reached with a single **local port forward** to StarRocks' MySQL-protocol port; [jdbcHost]/
 * [jdbcPort] then point at that local endpoint (`127.0.0.1:N`). [SshNoTunnelMethod] = direct.
 *
 * Only the JDBC connection is tunneled because, in a tunneled deployment, loading goes through the
 * **SQL `load_method`** (which runs over this same JDBC connection) rather than HTTP Stream Load —
 * Stream Load's FE→BE 307 redirect cannot be carried by a single local forward. So this is a thin
 * wrapper over the CDK's [createTunnelSession] (no SOCKS/dynamic forwarding needed). [close] tears
 * the tunnel down (it is closed at Micronaut context shutdown via AutoCloseable).
 */
class StarrocksSshTunnel(
    tunnelMethod: SshTunnelMethodConfiguration,
    starrocksHost: String,
    starrocksJdbcPort: Int,
) : AutoCloseable {

    /** JDBC host to connect to: the local forward when tunneling, else the configured host. */
    val jdbcHost: String
    /**
     * JDBC port to connect to: the local forward's port when tunneling, else the configured port.
     */
    val jdbcPort: Int

    private val tunnelSession: TunnelSession?

    init {
        if (tunnelMethod is SshNoTunnelMethod) {
            jdbcHost = starrocksHost
            jdbcPort = starrocksJdbcPort
            tunnelSession = null
        } else {
            val session =
                createTunnelSession(
                    SshdSocketAddress(starrocksHost, starrocksJdbcPort),
                    tunnelMethod,
                    SshConnectionOptions.fromAdditionalProperties(emptyMap()),
                )
            jdbcHost = session.address.hostString
            jdbcPort = session.address.port
            tunnelSession = session
            log.info {
                "SSH tunnel up: JDBC $starrocksHost:$starrocksJdbcPort via local forward $jdbcHost:$jdbcPort"
            }
        }
    }

    override fun close() {
        tunnelSession?.close()
    }
}
