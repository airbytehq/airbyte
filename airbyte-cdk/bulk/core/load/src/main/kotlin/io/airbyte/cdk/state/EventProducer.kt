/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import java.util.concurrent.ConcurrentLinkedQueue
import kotlinx.coroutines.channels.Channel

/**
 * A single-writer event producer for a multi-reader consumer.
 *
 * To use
 * - declare a subclass of [EventProducer] with the type parameter of the events to produce
 * - mark it `@Singleton` (single-writer!)
 * - configure [EventConsumer]s as described in the consumer's documentation
 * - inject the producer and consumers where needed
 *
 * TODO: If we need to support different paradigms (multi-writer, etc.), abstract this into an
 * interface and provide abstract implementations for each type.
 */
abstract class EventProducer<T> {
    private val subscribers = ConcurrentLinkedQueue<Channel<T>>()

    fun subscribe(): Channel<T> {
        val channel = Channel<T>(Channel.UNLIMITED)
        subscribers.add(channel)
        return channel
    }

    suspend fun produce(event: T) {
        subscribers.forEach { it.send(event) }
    }
}
