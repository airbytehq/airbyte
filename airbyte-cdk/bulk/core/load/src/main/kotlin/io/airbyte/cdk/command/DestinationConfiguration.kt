/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.nio.file.Path

abstract class DestinationConfiguration : Configuration {
    open val recordBatchSizeBytes: Long = 200L * 1024L * 1024L
    open val tmpFileDirectory: Path = Path.of("airbyte-cdk-load")
    open val firstStageTmpFilePrefix: String = "staged-raw-records"
    open val firstStageTmpFileSuffix: String = ".jsonl"

    /** Memory queue settings */
    open val maxMessageQueueMemoryUsageRatio: Double = 0.2 // 0 => No limit, 1.0 => 100% of JVM heap
    open val estimatedRecordMemoryOverheadRatio: Double =
        0.1 // 0 => No overhead, 1.0 => 100% overhead

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
