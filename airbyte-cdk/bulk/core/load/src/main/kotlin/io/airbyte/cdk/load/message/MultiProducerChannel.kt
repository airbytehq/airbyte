/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.channels.Channel

/**
 * A channel designed for use with a fixed amount of producers. Close will be called on the
 * underlying channel, when there are no remaining registered producers.
 */
class MultiProducerChannel<T>(
    producerCount: Long,
    channel: Channel<T>,
    private val name: String,
) : ChannelMessageQueue<T>(channel = channel) {
    private val log = KotlinLogging.logger {}
    private val initializedProducerCount = producerCount
    private val producerCount = AtomicLong(producerCount)

    override suspend fun close() {
        val count = producerCount.decrementAndGet()
        log.info {
            "Closing producer $name (active count=$count, initialized count: $initializedProducerCount)"
        }
        if (count == 0L) {
            log.info { "Closing underlying queue" }
            channel.close()
        }
    }
}
