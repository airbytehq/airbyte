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
// The word "Configuration" is overloaded.
// Consider either making this part of the DestinationConfiguration itself
// or renaming it to something less confusing.
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
// Groups of quasi-constants like these should be injected using @ConfigurationProperties,
// it's so much more convenient!
// See DefaultJdbcConstants for an example of what I mean.
open class DefaultWriteConfiguration : WriteConfiguration {
    override val recordBatchSizeBytes: Long = 200L * 1024L * 1024L
    override val firstStageTmpFilePrefix = "airbyte-cdk-load-staged-raw-records"

    override val maxMessageQueueMemoryUsageRatio: Double = 0.2
    override val estimatedRecordMemoryOverheadRatio: Double = 0.1
}
