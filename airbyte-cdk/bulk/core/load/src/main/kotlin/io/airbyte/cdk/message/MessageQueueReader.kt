/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.DestinationStream
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * A reader should provide a byte-limited flow of messages of the underlying type. The flow should
 * terminate when maxBytes has been read, or when the stream is complete.
 */
interface MessageQueueReader<K, T> {
    suspend fun readChunk(key: K, maxBytes: Long): Flow<T>
}

@Singleton
class DestinationMessageQueueReader(
    private val messageQueue: DestinationMessageQueue,
) : MessageQueueReader<DestinationStream, DestinationRecordWrapped> {
    private val log = KotlinLogging.logger {}

    override suspend fun readChunk(
        key: DestinationStream,
        maxBytes: Long
    ): Flow<DestinationRecordWrapped> = flow {
        log.info { "Reading chunk of $maxBytes bytes from stream $key" }

        var totalBytesRead = 0L
        var recordsRead = 0L
        while (totalBytesRead < maxBytes) {
            when (val wrapped = messageQueue.getChannel(key).receive()) {
                is StreamRecordWrapped -> {
                    totalBytesRead += wrapped.sizeBytes
                    emit(wrapped)
                }
                is StreamCompleteWrapped -> {
                    messageQueue.getChannel(key).close()
                    emit(wrapped)
                    log.info { "Read end-of-stream for $key" }
                    return@flow
                }
            }
            recordsRead++
        }

        log.info { "Read $recordsRead records (${totalBytesRead}b) from stream $key" }

        return@flow
    }
}
