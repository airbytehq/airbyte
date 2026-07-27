/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RedshiftConfigurationFactoryTest {

    private val factory = RedshiftConfigurationFactory()

    private fun spec(
        host: String = "my-cluster.redshift.amazonaws.com",
        port: Int = 5439,
        database: String = "mydb",
        schema: String = "public",
        username: String = "admin",
        password: String = "secret123",
        jdbcUrlParams: String? = null,
        hasUploadingMethod: Boolean = false,
        tunnelMethodValue: SshTunnelMethodConfiguration? = SshNoTunnelMethod,
        dropCascade: Boolean? = false,
    ): RedshiftSpecification = mockk {
        every { this@mockk.host } returns host
        every { this@mockk.port } returns port
        every { this@mockk.database } returns database
        every { this@mockk.schema } returns schema
        every { this@mockk.username } returns username
        every { this@mockk.password } returns password
        every { this@mockk.jdbcUrlParams } returns jdbcUrlParams
        every { this@mockk.uploadingMethod } returns if (hasUploadingMethod) mockk() else null
        every { getTunnelMethodValue() } returns tunnelMethodValue
        every { this@mockk.dropCascade } returns dropCascade
    }

    @Test
    fun `maps all fields from specification to configuration`() {
        val spec =
            spec(
                host = "my-cluster.abc123.us-east-1.redshift.amazonaws.com",
                port = 5440,
                database = "analytics",
                schema = "raw_data",
                username = "etl_user",
                password = "p@ssw0rd!",
                jdbcUrlParams = "ssl=true&timeout=30",
                hasUploadingMethod = true,
                tunnelMethodValue = SshNoTunnelMethod,
                dropCascade = true,
            )

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals("my-cluster.abc123.us-east-1.redshift.amazonaws.com", config.host)
        assertEquals(5440, config.port)
        assertEquals("analytics", config.database)
        assertEquals("raw_data", config.schema)
        assertEquals("etl_user", config.username)
        assertEquals("p@ssw0rd!", config.password)
        assertEquals("ssl=true&timeout=30", config.jdbcUrlParams)
        assertNotNull(config.uploadingMethod)
        assertEquals(SshNoTunnelMethod, config.tunnelMethod)
        assertEquals(true, config.dropCascade)
    }

    @Test
    fun `maps null optional fields`() {
        val spec =
            spec(
                jdbcUrlParams = null,
                hasUploadingMethod = false,
                tunnelMethodValue = null,
            )

        val config = factory.makeWithoutExceptionHandling(spec)

        assertNull(config.jdbcUrlParams)
        assertNull(config.uploadingMethod)
        assertNull(config.tunnelMethod)
        assertEquals(false, config.dropCascade)
    }

    @Test
    fun `maps SSH key auth tunnel method`() {
        val sshTunnel =
            SshKeyAuthTunnelMethod(
                host = "bastion.example.com",
                port = 22,
                user = "ec2-user",
                key = "-----BEGIN RSA PRIVATE KEY-----\nfakekey\n-----END RSA PRIVATE KEY-----",
            )
        val spec = spec(tunnelMethodValue = sshTunnel)

        val config = factory.makeWithoutExceptionHandling(spec)

        assertTrue(config.tunnelMethod is SshKeyAuthTunnelMethod)
        val tunnel = config.tunnelMethod as SshKeyAuthTunnelMethod
        assertEquals("bastion.example.com", tunnel.host)
        assertEquals(22, tunnel.port)
        assertEquals("ec2-user", tunnel.user)
    }

    @Test
    fun `maps SSH password auth tunnel method`() {
        val sshTunnel =
            SshPasswordAuthTunnelMethod(
                host = "jump-server.example.com",
                port = 2222,
                user = "tunnel-user",
                password = "tunnel-pass",
            )
        val spec = spec(tunnelMethodValue = sshTunnel)

        val config = factory.makeWithoutExceptionHandling(spec)

        assertTrue(config.tunnelMethod is SshPasswordAuthTunnelMethod)
        val tunnel = config.tunnelMethod as SshPasswordAuthTunnelMethod
        assertEquals("jump-server.example.com", tunnel.host)
        assertEquals(2222, tunnel.port)
        assertEquals("tunnel-user", tunnel.user)
        assertEquals("tunnel-pass", tunnel.password)
    }

    @Test
    fun `dropCascade defaults to false when null`() {
        val spec = spec(dropCascade = null)

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals(false, config.dropCascade)
    }

    @Test
    fun `uses spec default values`() {
        val spec = spec()

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals(5439, config.port)
        assertEquals("public", config.schema)
        assertEquals(false, config.dropCascade)
    }
}
