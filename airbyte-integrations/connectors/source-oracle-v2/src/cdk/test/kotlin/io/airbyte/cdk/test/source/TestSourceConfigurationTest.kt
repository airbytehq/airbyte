/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.LimitState
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class TestSourceConfigurationTest {

    @Inject lateinit var actual: SourceConfiguration

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.schemas", value = "PUBLIC,TESTSCHEMA")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_method",
        value = "SSH_PASSWORD_AUTH"
    )
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "22")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_user_password",
        value = "secret"
    )
    fun testVanilla() {
        val expected =
            TestSourceConfiguration(
                realHost = "localhost",
                realPort = 9092,
                sshTunnel = SshPasswordAuthTunnelMethod("localhost", 22, "sshuser", "secret"),
                sshConnectionOptions =
                    SshConnectionOptions(1_000.milliseconds, 2_000.milliseconds, Duration.ZERO),
                jdbcUrlFmt = "jdbc:h2:tcp://%s:%d/mem:testdb",
                schemas = setOf("PUBLIC", "TESTSCHEMA"),
                cursor = UserDefinedCursor,
                resumablePreferred = true,
                workerConcurrency = 1,
                workUnitSoftTimeout = java.time.Duration.ZERO,
                initialLimit = LimitState.minimum,
            )
        Assertions.assertEquals(expected, actual)
    }
}
