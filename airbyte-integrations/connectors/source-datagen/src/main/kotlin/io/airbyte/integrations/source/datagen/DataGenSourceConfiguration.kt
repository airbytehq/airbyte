/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.source.datagen.log
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.toJavaDuration

private val log = KotlinLogging.logger {}

/** Dev data gen-specific implementation of [SourceConfiguration] */
data class DataGenSourceConfiguration(
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = 0.seconds.toJavaDuration(),
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val realHost: String = "unused",
    override val realPort: Int = 0,
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
    //val flavor:
) : SourceConfiguration

@Singleton
class DataGenSourceConfigurationFactory:
    SourceConfigurationFactory<DataGenSourceConfigurationSpecification, DataGenSourceConfiguration> {

    override fun makeWithoutExceptionHandling(pojo: DataGenSourceConfigurationSpecification):
        DataGenSourceConfiguration {
        val maxConcurrency: Int = 1
        // TODO: support multi-threaded datagen
//            when (DataChannelMedium.valueOf(dataChannelMedium)) {
//                STDIO -> maxDBConnections ?: maxConcurrencyLegacy
//                SOCKET -> {
//                    maxDBConnections ?: maxConcurrencyLegacy.takeIf { it != 1 } ?: socketPaths.size
//                }
//            }
        log.info { "Effective concurrency: $maxConcurrency" }
        return DataGenSourceConfiguration(maxConcurrency = maxConcurrency)
    }
}
