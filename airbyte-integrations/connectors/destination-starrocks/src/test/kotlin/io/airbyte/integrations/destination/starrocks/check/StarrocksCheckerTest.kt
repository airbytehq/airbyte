/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.check

import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Guards the tunnel/load-method compatibility rule enforced by `check`: a configured SSH tunnel
 * only forwards the JDBC plane, so Stream Load (HTTP) is unreachable through it and the SQL load
 * method is required (#68). The DB-touching probes (validateStreamLoad/validateSqlLoad) are covered
 * by e2e.
 */
class StarrocksCheckerTest {

    private val tunnel =
        SshKeyAuthTunnelMethod("bastion.example", 22, "ec2-user", "-----BEGIN KEY-----")

    @Test
    fun `no tunnel is compatible with either load method`() {
        assertTrue(tunnelLoadMethodCompatible(SshNoTunnelMethod, loadAsSql = false))
        assertTrue(tunnelLoadMethodCompatible(SshNoTunnelMethod, loadAsSql = true))
    }

    @Test
    fun `a tunnel is only compatible with the SQL load method`() {
        // Stream Load's HTTP data plane cannot traverse the JDBC-only tunnel.
        assertFalse(tunnelLoadMethodCompatible(tunnel, loadAsSql = false))
        assertTrue(tunnelLoadMethodCompatible(tunnel, loadAsSql = true))
    }
}
