/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

/**
 * A multi-reader consumer of events produced by a single-writer [EventProducer].
 *
 * To use:
 * - set up an [EventProducer] with the same type parameter as described in the producer's
 * documentation
 * - declare a subclass of [EventConsumer] and mark it `@Prototype` (multi-reader)
 * - inject the producer and consumers where needed
 */
abstract class EventConsumer<T>(producer: EventProducer<T>) {
    val channel = producer.subscribe()

    suspend fun consumeMaybe(): T? {
        return channel.tryReceive().getOrNull()
    }
}
