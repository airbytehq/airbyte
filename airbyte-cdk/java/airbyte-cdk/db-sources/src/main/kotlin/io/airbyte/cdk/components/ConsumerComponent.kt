/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components

import java.util.function.Consumer

/**
 * [ConsumerComponent] collects records of type [R] produced by [ProducerComponent]. It's this
 * object's responsibility to tell the [ProducerComponent] that it has collected enough records.
 *
 * All implementations must be thread-safe. The [Consumer.accept] and [shouldCheckpoint] methods may
 * be called concurrently from multiple threads.
 */
interface ConsumerComponent<R> : Consumer<R> {

    /**
     * Returns true if the records held by this [ConsumerComponent] should be flushed ASAP. This
     * method is called by the [ProducerComponent] bound to this [ConsumerComponent].
     */
    fun shouldCheckpoint(): Boolean

    /**
     * Returns all the records accepted by the [ConsumerComponent]. This method is called
     * exclusively, and at most once, by [ComponentRunner.collect].
     */
    fun flush(): Sequence<R>

    fun interface Builder<R> {

        /**
         * Deterministically instantiates a new [ConsumerComponent] instance. May be called multiple
         * times. Called exclusively by [ComponentRunner].
         */
        fun build(): ConsumerComponent<R>
    }
}
