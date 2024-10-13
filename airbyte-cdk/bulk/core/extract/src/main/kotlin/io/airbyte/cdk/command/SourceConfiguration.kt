/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

/** Subtype of [Configuration] for sources. */
interface SourceConfiguration : Configuration, SshTunnelConfiguration {
    /** Does READ generate states of type GLOBAL? */
    val global: Boolean

    /** Maximum amount of time may be set to limit overall snapshotting duration */
    val maxSnapshotReadDuration: Duration?

    /** During the READ operation, how often a feed should checkpoint, ideally. */
    val checkpointTargetInterval: Duration

    /** Reader concurrency configuration. */
    val maxConcurrency: Int
    val resourceAcquisitionHeartbeat: Duration

    /**
     * Micronaut factory which glues [ConfigurationSpecificationSupplier] and
     * [SourceConfigurationFactory] together to produce a [SourceConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationSpecification> sourceConfig(
            pojoSupplier: ConfigurationSpecificationSupplier<I>,
            factory: SourceConfigurationFactory<I, out SourceConfiguration>,
        ): SourceConfiguration = factory.make(pojoSupplier.get())
    }
}
