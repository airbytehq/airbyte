/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

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

/** [SourceConfiguration] implementation for a fake source. */
data class FakeSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration,
    override val sshConnectionOptions: SshConnectionOptions,
    val cursor: CursorConfiguration,
    override val maxConcurrency: Int,
    override val checkpointTargetInterval: Duration,
) : SourceConfiguration {
    override val global: Boolean = cursor is CdcCursor

    override val resourceAcquisitionHeartbeat: Duration
        get() = Duration.ofMillis(10)
}

/** [SourceConfigurationFactory] implementation for a fake source. */
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
            cursor = pojo.getCursorConfigurationValue() ?: UserDefinedCursor,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.parse(pojo.timeout).takeIf { it.isPositive }
                    ?: Duration.ofDays(100L),
        )
    }
}
