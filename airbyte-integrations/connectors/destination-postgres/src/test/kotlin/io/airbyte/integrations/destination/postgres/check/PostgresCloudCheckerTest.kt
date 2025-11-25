/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.check

import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.spec.SslMode
import io.airbyte.integrations.destination.postgres.spec.SslModeAllow
import io.airbyte.integrations.destination.postgres.spec.SslModeDisable
import io.airbyte.integrations.destination.postgres.spec.SslModePrefer
import io.airbyte.integrations.destination.postgres.spec.SslModeRequire
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyCa
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyFull
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

internal class PostgresCloudCheckerTest {
    private lateinit var postgresConfiguration: PostgresConfiguration
    private lateinit var ossChecker: PostgresOssChecker
    private lateinit var checker: PostgresCloudChecker

    @BeforeEach
    fun setup() {
        postgresConfiguration = mockk()
        ossChecker = mockk()
    }

    companion object {
        @JvmStatic
        fun secureSSLModes() = listOf(SslModeRequire(), SslModeVerifyCa(), SslModeVerifyFull())

        @JvmStatic
        fun insecureSSLModes() = listOf(SslModeDisable(), SslModeAllow(), SslModePrefer())
    }

    @ParameterizedTest
    @MethodSource("secureSSLModes")
    fun testCheckSucceedsNoTunnel(sslMode: SslMode) {
        every { postgresConfiguration.tunnelMethod } returns SshNoTunnelMethod
        every { postgresConfiguration.sslMode } returns sslMode
        every { ossChecker.check() } just runs

        checker = PostgresCloudChecker(postgresConfiguration, ossChecker)
        checker.check()

        verify(exactly = 1) { ossChecker.check() }
    }

    @Test
    fun testCheckSucceedsTunnelMethod() {
        every { postgresConfiguration.tunnelMethod } returns
            SshKeyAuthTunnelMethod(host = "localhost", port = 22, user = "user", key = "key")
        every { ossChecker.check() } just runs

        checker = PostgresCloudChecker(postgresConfiguration, ossChecker)
        checker.check()

        verify(exactly = 1) { ossChecker.check() }
    }

    @ParameterizedTest
    @MethodSource("insecureSSLModes")
    fun testCheckFailsNoTunnel(sslMode: SslMode) {
        every { postgresConfiguration.tunnelMethod } returns SshNoTunnelMethod
        every { postgresConfiguration.sslMode } returns sslMode

        checker = PostgresCloudChecker(postgresConfiguration, ossChecker)
        val exception = assertThrows<IllegalArgumentException> { checker.check() }

        assertTrue(exception.message!!.contains("Unsecured connection not allowed"))
        verify(exactly = 0) { ossChecker.check() }
    }

    @Test
    fun testCheckFailsOnOssChecker() {
        every { postgresConfiguration.tunnelMethod } returns SshNoTunnelMethod
        every { postgresConfiguration.sslMode } returns SslModeRequire()
        every { ossChecker.check() } throws IllegalStateException("Database connection failed")

        checker = PostgresCloudChecker(postgresConfiguration, ossChecker)
        val exception = assertThrows<IllegalStateException> { checker.check() }

        assertEquals("Database connection failed", exception.message)
        verify(exactly = 1) { ossChecker.check() }
    }
}
