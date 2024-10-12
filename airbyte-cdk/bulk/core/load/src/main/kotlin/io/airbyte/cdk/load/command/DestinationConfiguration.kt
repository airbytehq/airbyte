/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.command.Configuration
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
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
     * If we have not flushed state checkpoints in this amount of time, make a best-effort attempt
     * to force a flush.
     */
    open val maxCheckpointFlushTimeMs: Long = 15 * 60 * 1000L // 15 minutes

    /** The max number of threads to use for implementor tasks (e.g. open, processBatch). */
    open val maxNumImplementorTaskThreads = 64

    /**
     * The amount of time given to implementor tasks (e.g. open, processBatch) to complete their
     * current work after a failure.
     */
    open val gracefulCancellationTimeoutMs: Long = 60 * 1000L // 1 minutes

    /**
     * Micronaut factory which glues [ConfigurationSpecificationSupplier] and
     * [DestinationConfigurationFactory] together to produce a [DestinationConfiguration] singleton.
     */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun <I : ConfigurationSpecification> destinationConfig(
            specificationSupplier: ConfigurationSpecificationSupplier<I>,
            factory: DestinationConfigurationFactory<I, out DestinationConfiguration>,
        ): DestinationConfiguration = factory.make(specificationSupplier.get())
    }
}
