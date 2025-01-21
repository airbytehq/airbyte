/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.task.internal.ForceFlushEvent
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

interface FlushStrategy {
    suspend fun shouldFlush(
        stream: DestinationStream,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean
}

/**
 * Flush whenever
 * - bytes consumed >= the configured batch size
 * - the current range of indexes being consumed encloses a force flush index
 */
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
@Singleton
@Secondary
class DefaultFlushStrategy(
    private val config: DestinationConfiguration,
    private val eventQueue: QueueReader<ForceFlushEvent>
) : FlushStrategy {
    private val forceFlushIndexes = ConcurrentHashMap<DestinationStream.Descriptor, Long>()

    override suspend fun shouldFlush(
        stream: DestinationStream,
        rangeRead: Range<Long>,
        bytesProcessed: Long
    ): Boolean {
        if (bytesProcessed >= config.recordBatchSizeBytes) {
            return true
        }

        // Listen to the event stream for a new force flush index
        val nextFlushIndex = eventQueue.poll()?.indexes?.get(stream.descriptor)

        // Always update the index if the new one is not null
        return when (
            val testIndex =
                forceFlushIndexes.compute(stream.descriptor) { _, v -> nextFlushIndex ?: v }
        ) {
            null -> false
            else -> rangeRead.contains(testIndex)
        }
    }
}
