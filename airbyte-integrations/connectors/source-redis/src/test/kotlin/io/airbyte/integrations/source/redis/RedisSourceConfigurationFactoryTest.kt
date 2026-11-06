/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class RedisSourceConfigurationFactoryTest {
    @Test
    fun testDefaultsAndStdioConcurrency() {
        val config = factory().make(spec())
        Assertions.assertEquals(6379, config.port)
        Assertions.assertEquals(0, config.database)
        Assertions.assertEquals("*", config.keyPattern)
        Assertions.assertEquals(1000, config.scanBatchSize)
        Assertions.assertEquals(1, config.maxConcurrency)
    }

    @Test
    fun testWhitespacePasswordIsPreserved() {
        val config = factory().make(spec().apply { password = " " })
        Assertions.assertEquals(" ", config.password)
    }

    @Test
    fun testEmptyPasswordIsDiscarded() {
        val config = factory().make(spec().apply { password = "" })
        Assertions.assertNull(config.password)
    }

    @Test
    fun testSocketConcurrencyDefaultsToSocketCount() {
        val config = factory("SOCKET", listOf("/tmp/a", "/tmp/b")).make(spec())
        Assertions.assertEquals(2, config.maxConcurrency)
    }

    @Test
    fun testInvalidPortIsRejected() {
        assertInvalid { it.port = 65536 }
    }

    @Test
    fun testNegativeDatabaseIsRejected() {
        assertInvalid { it.database = -1 }
    }

    @Test
    fun testInvalidScanBatchSizeIsRejected() {
        assertInvalid { it.scanBatchSize = 0 }
    }

    @Test
    fun testInvalidMaxDbConnectionsIsRejected() {
        assertInvalid { it.maxDbConnections = 0 }
    }

    @Test
    fun testVerifyFullCannotUseSshTunnel() {
        val ssl = RedisSslVerifyFull()
        val specification =
            spec().apply {
                setSslModeValue(ssl)
                setTunnelMethodValue(SshKeyAuthTunnelMethod("jump.example", 22, "airbyte", "key"))
            }
        val exception =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                factory().make(specification)
            }
        Assertions.assertTrue(exception.message!!.contains("Use 'verify-ca' instead"))
    }

    @Test
    fun testZeroSocketPathsAreRejectedWhenConcurrencyIsNotConfigured() {
        val exception =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                factory("SOCKET", emptyList()).make(spec())
            }
        Assertions.assertTrue(exception.message!!.contains("must be positive"))
    }

    private fun assertInvalid(change: (RedisSourceConfigurationSpecification) -> Unit) {
        val specification = spec()
        change(specification)
        Assertions.assertThrows(ConfigErrorException::class.java) { factory().make(specification) }
    }

    private fun factory(
        medium: String = "STDIO",
        socketPaths: List<String> = emptyList(),
    ) = RedisSourceConfigurationFactory(medium, socketPaths)

    private fun spec() = RedisSourceConfigurationSpecification().apply { host = "localhost" }
}
