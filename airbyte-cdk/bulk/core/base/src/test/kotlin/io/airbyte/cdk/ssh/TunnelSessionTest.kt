/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import io.airbyte.cdk.ConfigErrorException
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkAll
import io.mockk.verify
import org.apache.sshd.client.SshClient
import org.apache.sshd.client.future.ConnectFuture
import org.apache.sshd.client.session.ClientSession
import org.apache.sshd.common.keyprovider.KeyIdentityProvider
import org.apache.sshd.common.util.net.SshdSocketAddress
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import java.net.InetSocketAddress
import java.security.KeyPair

class TunnelSessionTest {

    private val testRemoteHost = "database.example.com"
    private val testRemotePort = 5432
    private val testSshHost = "bastion.example.com"
    private val testSshPort = 22
    private val testSshUser = "ssh-user"
    private val testSshPassword = "ssh-password"
    private val testSshKey = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""

    @BeforeEach
    fun setUp() {
        // Reset mocks before each test
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `test createTunnelSession with SshNoTunnelMethod returns direct connection`() {
        // Given
        val remote = SshdSocketAddress(testRemoteHost, testRemotePort)
        val sshTunnel = SshNoTunnelMethod
        val connectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap())

        // When
        val tunnelSession = createTunnelSession(remote, sshTunnel, connectionOptions)

        // Then
        assertNotNull(tunnelSession)
        assertEquals(testRemoteHost, tunnelSession.address.hostName)
        assertEquals(testRemotePort, tunnelSession.address.port)

        // Cleanup
        tunnelSession.close()
    }

    @Test
    fun `test createTunnelSession with null tunnel method throws IllegalStateException`() {
        // Given
        val remote = SshdSocketAddress(testRemoteHost, testRemotePort)
        val sshTunnel: SshTunnelMethodConfiguration? = null
        val connectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap())

        // When/Then - should throw IllegalStateException because null should have been handled by early return
        // Note: This tests the defensive programming check in the when expression
        val exception = assertThrows<IllegalStateException> {
            createTunnelSession(remote, sshTunnel, connectionOptions)
        }

        // Verify the exception message is descriptive
        assertNotNull(exception.message)
        assert(exception.message!!.contains("SSH tunnel method is null"))
    }

    @Test
    fun `test TunnelSession close with no client and session does nothing`() {
        // Given
        val address = InetSocketAddress.createUnresolved("localhost", 5432)
        val tunnelSession = TunnelSession(address, null, null)

        // When/Then - should not throw
        tunnelSession.close()
    }

    @Test
    fun `test TunnelSession close with client and session closes both`() {
        // Given
        val address = InetSocketAddress.createUnresolved("localhost", 5432)
        val mockClient = mockk<SshClient>(relaxed = true)
        val mockSession = mockk<ClientSession>(relaxed = true)
        val tunnelSession = TunnelSession(address, mockClient, mockSession)

        // When
        tunnelSession.close()

        // Then
        verify { mockSession.close() }
        verify { mockClient.stop() }
    }

    @Test
    fun `test TunnelSession address properties`() {
        // Given
        val host = "localhost"
        val port = 5432
        val address = InetSocketAddress.createUnresolved(host, port)

        // When
        val tunnelSession = TunnelSession(address, null, null)

        // Then
        assertEquals(host, tunnelSession.address.hostName)
        assertEquals(port, tunnelSession.address.port)
    }

    @Test
    fun `test SSH connection options defaults`() {
        // Given/When
        val options = SshConnectionOptions.fromAdditionalProperties(emptyMap())

        // Then
        assertNotNull(options)
        // Verify that default options are created without errors
    }

    @Test
    fun `test SshKeyAuthTunnelMethod contains all required fields`() {
        // Given/When
        val sshKeyAuth = SshKeyAuthTunnelMethod(
            host = testSshHost,
            port = testSshPort,
            user = testSshUser,
            key = testSshKey
        )

        // Then
        assertEquals(testSshHost, sshKeyAuth.host)
        assertEquals(testSshPort, sshKeyAuth.port)
        assertEquals(testSshUser, sshKeyAuth.user)
        assertEquals(testSshKey, sshKeyAuth.key)
    }

    @Test
    fun `test SshPasswordAuthTunnelMethod contains all required fields`() {
        // Given/When
        val sshPasswordAuth = SshPasswordAuthTunnelMethod(
            host = testSshHost,
            port = testSshPort,
            user = testSshUser,
            password = testSshPassword
        )

        // Then
        assertEquals(testSshHost, sshPasswordAuth.host)
        assertEquals(testSshPort, sshPasswordAuth.port)
        assertEquals(testSshUser, sshPasswordAuth.user)
        assertEquals(testSshPassword, sshPasswordAuth.password)
    }

    @Test
    fun `test SshNoTunnelMethod is singleton`() {
        // Given/When
        val instance1 = SshNoTunnelMethod
        val instance2 = SshNoTunnelMethod

        // Then
        assertEquals(instance1, instance2)
    }

    @Test
    fun `test SshdSocketAddress conversion to InetSocketAddress`() {
        // Given
        val sshdAddress = SshdSocketAddress(testRemoteHost, testRemotePort)

        // When
        val inetAddress = sshdAddress.toInetSocketAddress()

        // Then
        assertNotNull(inetAddress)
        assertEquals(testRemoteHost, inetAddress.hostName)
        assertEquals(testRemotePort, inetAddress.port)
    }
}
