/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.github.oshai.kotlinlogging.KotlinLogging
import java.lang.IllegalStateException
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.channels.Channel

/**
 * A channel designed for use with a dynamic amount of producers. Close will only close the
 * underlying channel, when there are no remaining registered producers.
 */
class MultiProducerChannel<T>(override val channel: Channel<T>) : ChannelMessageQueue<T>() {
    private val log = KotlinLogging.logger {}
    private val producerCount = AtomicLong(0)
    private val closed = AtomicBoolean(false)

    fun registerProducer(): MultiProducerChannel<T> {
        if (closed.get()) {
            throw IllegalStateException("Attempted to register producer for closed channel.")
        }

        val count = producerCount.incrementAndGet()
        log.info { "Registering producer (count=$count)" }
        return this
    }

    override suspend fun close() {
        val count = producerCount.decrementAndGet()
        log.info { "Closing producer (count=$count)" }
        if (count == 0L) {
            log.info { "Closing queue" }
            channel.close()
            closed.getAndSet(true)
        }
    }
}
