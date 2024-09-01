/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * General configuration for the write operation. The implementor can override this to tweak runtime
 * behavior.
 */
interface WriteConfiguration {
    /** Batch accumulation settings. */
    val recordBatchSizeBytes: Long
    val firstStageTmpFilePrefix: String

    /** Memory queue settings */
    val maxMessageQueueMemoryUsageRatio: Double // as fraction of available memory
    val estimatedRecordMemoryOverheadRatio: Double // 0 => No overhead, 1.0 => 2x overhead
}

@Singleton
@Secondary
open class DefaultWriteConfiguration : WriteConfiguration {
    override val recordBatchSizeBytes: Long = 200L * 1024L * 1024L
    override val firstStageTmpFilePrefix = "airbyte-cdk-load-staged-raw-records"

    override val maxMessageQueueMemoryUsageRatio: Double = 0.2
    override val estimatedRecordMemoryOverheadRatio: Double = 0.1
}
