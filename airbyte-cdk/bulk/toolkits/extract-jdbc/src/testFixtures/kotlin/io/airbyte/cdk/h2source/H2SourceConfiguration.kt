/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.h2source

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

/** [SourceConfiguration] implementation for [H2Source]. */
data class H2SourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val namespaces: Set<String>,
    val cursor: CursorConfiguration,
    val resumablePreferred: Boolean,
    override val maxConcurrency: Int,
    override val checkpointTargetInterval: Duration,
    override val maxSnapshotReadDuration: Duration? = null,
) : JdbcSourceConfiguration {
    override val global: Boolean = cursor is CdcCursor
    override val jdbcProperties: Map<String, String> = mapOf()

    override val resourceAcquisitionHeartbeat: Duration
        get() = Duration.ofMillis(10)
}

/** [SourceConfigurationFactory] implementation for [H2Source]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class H2SourceConfigurationFactory :
    SourceConfigurationFactory<H2SourceConfigurationSpecification, H2SourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: H2SourceConfigurationSpecification,
    ): H2SourceConfiguration {
        val sshConnectionOptions: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())
        return H2SourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = pojo.getTunnelMethodValue() ?: SshNoTunnelMethod,
            sshConnectionOptions = sshConnectionOptions,
            jdbcUrlFmt = "jdbc:h2:tcp://%s:%d/mem:${pojo.database}",
            namespaces = pojo.schemas?.takeUnless { it.isEmpty() }?.toSet() ?: setOf("PUBLIC"),
            cursor = pojo.getCursorConfigurationValue() ?: UserDefinedCursor,
            resumablePreferred = pojo.resumablePreferred != false,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.parse(pojo.timeout).takeIf { it.isPositive }
                    ?: Duration.ofDays(100L),
        )
    }
}
