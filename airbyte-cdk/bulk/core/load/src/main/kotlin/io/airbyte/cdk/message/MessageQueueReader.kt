/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.DestinationStream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * A reader should provide a byte-limited flow of messages of the underlying type. The flow should
 * terminate when maxBytes has been read, or when the stream is complete.
 */
interface MessageQueueReader<K, T> {
    suspend fun read(key: K): Flow<T>
}

@Singleton
@Secondary
class DestinationMessageQueueReader(
    private val messageQueue: DestinationMessageQueue,
) : MessageQueueReader<DestinationStream.Descriptor, DestinationRecordWrapped> {
    private val log = KotlinLogging.logger {}

    override suspend fun read(key: DestinationStream.Descriptor): Flow<DestinationRecordWrapped> =
        flow {
            log.info { "Reading from stream $key" }

            while (true) {
                when (val wrapped = messageQueue.getChannel(key).receive()) {
                    is StreamRecordWrapped -> {
                        emit(wrapped)
                    }
                    is StreamCompleteWrapped -> {
                        messageQueue.getChannel(key).close()
                        emit(wrapped)
                        log.info { "Read end-of-stream for $key" }
                        return@flow
                    }
                }
            }
        }
}
