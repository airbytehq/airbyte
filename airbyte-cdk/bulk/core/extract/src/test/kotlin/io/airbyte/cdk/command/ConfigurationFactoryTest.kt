/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.fakesource.FakeSourceConfiguration
import io.airbyte.cdk.fakesource.UserDefinedCursor
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
class ConfigurationFactoryTest {
    @Inject lateinit var actual: SourceConfiguration

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.schemas", value = "PUBLIC,TESTSCHEMA")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_method",
        value = "SSH_PASSWORD_AUTH",
    )
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "22")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_user_password",
        value = "secret",
    )
    fun testVanilla() {
        val expected =
            FakeSourceConfiguration(
                realHost = "localhost",
                realPort = 9092,
                sshTunnel = SshPasswordAuthTunnelMethod("localhost", 22, "sshuser", "secret"),
                sshConnectionOptions =
                    SshConnectionOptions(1_000.milliseconds, 2_000.milliseconds, Duration.ZERO),
                cursor = UserDefinedCursor,
                maxConcurrency = 1,
                checkpointTargetInterval = java.time.Duration.ofDays(100L),
            )
        Assertions.assertEquals(expected, actual)
    }
}
