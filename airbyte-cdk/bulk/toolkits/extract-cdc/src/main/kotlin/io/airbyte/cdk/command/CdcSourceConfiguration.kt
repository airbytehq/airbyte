/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.time.Duration

/** CDC-specific flavor of [SourceConfiguration]. */
interface CdcSourceConfiguration : SourceConfiguration {

    /**
     * How often Debezium is to emit heartbeat events.
     *
     * This value is typically much lower in tests than in production.
     */
    val debeziumHeartbeatInterval: Duration

    /**
     * Micronaut factory which glues [ConfigurationJsonObjectSupplier] and
     * [SourceConfigurationFactory] together to produce a [CdcSourceConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationSpecification> cdcSourceConfig(
            pojoSupplier: ConfigurationSpecificationSupplier<I>,
            factory: SourceConfigurationFactory<I, out CdcSourceConfiguration>,
        ): CdcSourceConfiguration = factory.make(pojoSupplier.get())
    }
}
