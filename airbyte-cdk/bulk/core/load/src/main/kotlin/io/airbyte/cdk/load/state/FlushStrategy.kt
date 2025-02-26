/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

interface FlushStrategy {
    suspend fun shouldFlush(
        stream: DestinationStream.Descriptor,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean
}

/**
 * Flush whenever
 * - bytes consumed >= the configured batch size
 */
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
@Secondary
class DefaultFlushStrategy(
    private val config: DestinationConfiguration,
    @Value("\${airbyte.destination.core.record-batch-size-override}")
    private val recordBatchSizeOverride: Long? = null
) : FlushStrategy {
    override suspend fun shouldFlush(
        stream: DestinationStream.Descriptor,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean = bytesProcessed >= (recordBatchSizeOverride ?: config.recordBatchSizeBytes)
}
