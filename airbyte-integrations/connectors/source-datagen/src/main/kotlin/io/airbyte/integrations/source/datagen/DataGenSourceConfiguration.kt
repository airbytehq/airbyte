/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.source.datagen.flavor.Flavor
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor
import io.airbyte.integrations.source.datagen.flavor.types.TypesFlavor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.toJavaDuration

/** Dev data gen-specific implementation of [SourceConfiguration] */
data class DataGenSourceConfiguration(
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = 10.seconds.toJavaDuration(),
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val realHost: String = "unused",
    override val realPort: Int = 0,
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
    val flavor: Flavor,
    val maxRecords: Long
) : SourceConfiguration {
    /** Required to inject [DataGenSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun dataGenSourceConfig(
            factory:
                SourceConfigurationFactory<
                    DataGenSourceConfigurationSpecification, DataGenSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<DataGenSourceConfigurationSpecification>,
        ): DataGenSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class DataGenSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList()
) :
    SourceConfigurationFactory<
        DataGenSourceConfigurationSpecification, DataGenSourceConfiguration> {

    private val log = KotlinLogging.logger {}

    override fun makeWithoutExceptionHandling(
        pojo: DataGenSourceConfigurationSpecification
    ): DataGenSourceConfiguration {
        if ((pojo.concurrency ?: 1) <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> pojo.concurrency ?: 1
                SOCKET -> {
                    pojo.concurrency ?: socketPaths.size
                }
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        val flavorSpec = pojo.getFlavor()
        val flavor: Flavor =
            when (flavorSpec) {
                Incremental -> IncrementFlavor
                Types -> TypesFlavor
            }

        return DataGenSourceConfiguration(
            maxConcurrency = maxConcurrency,
            flavor = flavor,
            maxRecords = pojo.maxRecords
        )
    }
}
