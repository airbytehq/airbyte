/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import io.airbyte.cdk.command.ConfigurationFactory
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

/** [SourceConfiguration] implementation for [TestSource]. */
data class TestSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val schemas: Set<String>,
    val cursor: CursorConfiguration,
) : SourceConfiguration {

    override val workerConcurrency: Int = 1
    override val workUnitSoftTimeout: Duration = Duration.ZERO

    override val global: Boolean = cursor is CdcCursor
    override val jdbcProperties: Map<String, String> = mapOf()
}

/** [ConfigurationFactory] implementation for [TestSource]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class TestSourceConfigurationFactory :
    ConfigurationFactory<TestSourceConfigurationJsonObject, TestSourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: TestSourceConfigurationJsonObject
    ): TestSourceConfiguration {
        val sshConnectionOptions: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
        return TestSourceConfiguration(
            realHost = pojo.host!!,
            realPort = pojo.port!!,
            sshTunnel = pojo.getTunnelMethodValue(),
            sshConnectionOptions = sshConnectionOptions,
            jdbcUrlFmt = "jdbc:h2:tcp://%s:%d/mem:${pojo.database!!}",
            schemas = pojo.schemas.takeUnless { it.isEmpty() }!!.toSet(),
            cursor = pojo.getCursorConfigurationValue(),
        )
    }
}
