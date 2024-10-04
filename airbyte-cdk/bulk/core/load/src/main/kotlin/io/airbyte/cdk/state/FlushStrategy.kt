/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface FlushStrategy {
    suspend fun shouldFlush(
        stream: DestinationStream,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean
}

@Singleton
@Secondary
class DefaultFlushStrategy(
    private val config: DestinationConfiguration,
) : FlushStrategy {

    override suspend fun shouldFlush(
        stream: DestinationStream,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean {
        return bytesProcessed >= config.recordBatchSizeBytes
    }
}
