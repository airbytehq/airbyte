/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.tunnel

import io.airbyte.cdk.ssh.SshNoTunnelMethod
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class StarrocksSshTunnelTest {

    @Test
    fun `no-tunnel method passes the StarRocks endpoint through and opens no session`() {
        StarrocksSshTunnel(SshNoTunnelMethod, "starrocks.example.com", 9030).use { tunnel ->
            assertEquals("starrocks.example.com", tunnel.jdbcHost)
            assertEquals(9030, tunnel.jdbcPort)
        }
        // close() on a no-tunnel instance is a no-op and must not throw.
    }
}
