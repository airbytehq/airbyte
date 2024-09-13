/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

interface DestinationConfiguration : Configuration {
    val recordBatchSizeBytes: Long
    val firstStageTmpFilePrefix: String

    /** Memory queue settings */
    val maxMessageQueueMemoryUsageRatio: Double // as fraction of available memory
    val estimatedRecordMemoryOverheadRatio: Double // 0 => No overhead, 1.0 => 2x overhead

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

    companion object {
        const val DEFAULT_RECORD_BATCH_SIZE_BYTES: Long = 200L * 1024L * 1024L
        const val DEFAULT_FIRST_STAGE_TMP_FILE_PREFIX = "airbyte-cdk-load-staged-raw-records"
        const val DEFAULT_MAX_MESSAGE_QUEUE_MEMORY_USAGE_RATIO: Double = 0.2
        const val DEFAULT_ESTIMATED_RECORD_MEMORY_OVERHEAD_RATIO: Double = 0.1
    }
}
