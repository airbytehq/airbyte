/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components

/**
 * [ProducerComponent] is a [Runnable] which runs indefinitely to produce records and pass them to a
 * [ConsumerComponent]. [Runnable.run] only stops after [AutoCloseable.close] is called.
 * [AutoCloseable.close] will be called exactly once and not before [Runnable.run].
 *
 * All implementations must be thread-safe. All methods will be called in different threads and
 * exclusively by the [ComponentRunner].
 */
interface ProducerComponent<S> : Runnable, AutoCloseable {

    /**
     * Returns the final state of the producer. Starting a new producer using this state as its
     * initial state will resume production where it left off. This method will be called after the
     * call to [Runnable.run] completes.
     */
    fun finalState(): S

    fun interface Builder<R, S> {

        /**
         * Deterministically instantiates a new [ProducerComponent] instance:
         * - [input] is the initial state of the producer and determines which records of type [R]
         * will be produced;
         * - [consumer] is the consumer to pass the records to via [ConsumerComponent.accept];
         * - [notifyStop] is the callback that the producer will call when it thinks that it should
         * stop producing, typically when [ConsumerComponent.shouldCheckpoint] returns true.
         *
         * May be called multiple times. Called exclusively by [ComponentRunner].
         */
        fun build(
            input: S,
            consumer: ConsumerComponent<R>,
            notifyStop: () -> Unit,
        ): ProducerComponent<S>
    }
}
