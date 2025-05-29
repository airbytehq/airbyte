/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

/** Subtype of [Configuration] for sources. */
interface SourceConfiguration : Configuration, SshTunnelConfiguration {
    /** Does READ generate states of type GLOBAL? */
    val global: Boolean

    /** During the READ operation, how often a feed should checkpoint, ideally. */
    val checkpointTargetInterval: Duration

    /** Reader concurrency configuration. */
    val maxConcurrency: Int
    val resourceAcquisitionHeartbeat: Duration

    /**
     * Micronaut factory which glues [ConfigurationJsonObjectSupplier] and
     * [SourceConfigurationFactory] together to produce a [SourceConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationJsonObjectBase> sourceConfig(
            pojoSupplier: ConfigurationJsonObjectSupplier<I>,
            factory: SourceConfigurationFactory<I, out SourceConfiguration>,
        ): SourceConfiguration = factory.make(pojoSupplier.get())
    }
}
