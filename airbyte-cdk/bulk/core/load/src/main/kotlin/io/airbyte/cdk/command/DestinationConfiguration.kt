/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

abstract class DestinationConfiguration : Configuration {
    val recordBatchSizeBytes: Long = 200L * 1024L * 1024L
    val firstStageTmpFilePrefix: String = "airbyte-cdk-load-staged-raw-records"

    /** Memory queue settings */
    val maxMessageQueueMemoryUsageRatio: Double = 0.2 // 0 => No limit, 1.0 => 100% of JVM heap
    val estimatedRecordMemoryOverheadRatio: Double = 0.1 // 0 => No overhead, 1.0 => 100% overhead

    /**
     * Micronaut factory which glues [ConfigurationJsonObjectSupplier] and
     * [DestinationConfigurationFactory] together to produce a [DestinationConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationJsonObjectBase> destinationConfig(
            pojoSupplier: ConfigurationJsonObjectSupplier<I>,
            factory: DestinationConfigurationFactory<I, out DestinationConfiguration>,
        ): DestinationConfiguration {
            return factory.make(pojoSupplier.get())
        }
    }
}
