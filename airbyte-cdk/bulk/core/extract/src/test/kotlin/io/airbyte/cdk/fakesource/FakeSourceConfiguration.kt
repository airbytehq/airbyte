/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

/** [SourceConfiguration] implementation for [FakeSource]. */
data class FakeSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val schemas: Set<String>,
    val cursor: CursorConfiguration,
    val resumablePreferred: Boolean,
    override val maxConcurrency: Int,
    override val checkpointTargetInterval: Duration,
) : JdbcSourceConfiguration {
    override val global: Boolean = cursor is CdcCursor
    override val jdbcProperties: Map<String, String> = mapOf()

    override val resourceAcquisitionHeartbeat: Duration
        get() = Duration.ofMillis(10)
}

/** [SourceConfigurationFactory] implementation for [FakeSource]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class FakeSourceConfigurationFactory :
    SourceConfigurationFactory<FakeSourceConfigurationJsonObject, FakeSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: FakeSourceConfigurationJsonObject,
    ): FakeSourceConfiguration {
        val sshConnectionOptions: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
        return FakeSourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = pojo.getTunnelMethodValue() ?: SshNoTunnelMethod,
            sshConnectionOptions = sshConnectionOptions,
            jdbcUrlFmt = "jdbc:h2:tcp://%s:%d/mem:${pojo.database}",
            schemas = pojo.schemas?.takeUnless { it.isEmpty() }?.toSet() ?: setOf("PUBLIC"),
            cursor = pojo.getCursorConfigurationValue() ?: UserDefinedCursor,
            resumablePreferred = pojo.resumablePreferred != false,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.parse(pojo.timeout).takeIf { it.isPositive }
                    ?: Duration.ofDays(100L),
        )
    }
}
