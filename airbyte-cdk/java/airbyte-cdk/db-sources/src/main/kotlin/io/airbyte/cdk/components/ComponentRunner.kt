/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components

import java.time.Duration
import java.util.concurrent.atomic.AtomicReference
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * [ComponentRunner] orchestrates [ProducerComponent] and [ConsumerComponent] instances to collect
 * records and states.
 *
 * Constructor args:
 * - [name] is decorative-only and is used to name the threads spawned by this object;
 * - [producerBuilder] is used to instantiate [ProducerComponent];
 * - [consumerBuilder] is used to instantiate [ConsumerComponent];
 * - [maxTime] is the global timeout for a [collect] method call;
 * - [comparator] is used by [collectRepeatedly] to compare relative progress between two states.
 */
class ComponentRunner<R, S>(
    val name: String,
    val producerBuilder: ProducerComponent.Builder<R, S>,
    val consumerBuilder: ConsumerComponent.Builder<R>,
    val maxTime: Duration,
    val comparator: Comparator<S>,
) {

    /**
     * [collect] instantiates a [ProducerComponent] with a [ConsumerComponent] and uses them to
     * collect records until a stopping criterion is met.
     *
     * The [input] argument determines the records emitted by the producer. Either the producer
     * itself triggers a stop or the [maxTime] timeout does, after which we return:
     * - all records produced and consumed, with [ConsumerComponent.flush],
     * - the final state of the producer, with [ProducerComponent.finalState].
     */
    fun collect(input: S): Pair<Sequence<R>, S> {
        val consumer: ConsumerComponent<R> = consumerBuilder.build()
        val sentinel = Runnable {
            try {
                Thread.sleep(maxTime.toMillis())
                log.debug("$name timed out.")
            } catch (e: InterruptedException) {
                log.debug("$name was notified to stop before timing out.", e)
            } catch (e: Throwable) {
                log.warn("$name sentinel threw an error or an exception", e)
            }
        }
        val sentinelThread = Thread(sentinel, "$name-closer-sentinel")
        val producer: ProducerComponent<S> =
            producerBuilder.build(input, consumer, sentinelThread::interrupt)
        val producerThread = Thread(producer, "$name-producer")
        val closer = Runnable {
            try {
                sentinelThread.join()
                log.debug("$name timed out, closing...")
            } catch (e: InterruptedException) {
                log.debug("$name was notified to stop before timing out, closing...", e)
            }
            try {
                producer.close()
                log.debug("$name closed")
            } catch (e: Throwable) {
                log.warn("$name producer close() threw an exception", e)
                throw e
            }
        }
        val closerThread = Thread(closer, "$name-closer")
        val thrown = AtomicReference<Throwable>()
        log.debug("$name is running")
        sentinelThread.start()
        producerThread.setUncaughtExceptionHandler { _, e: Throwable ->
            thrown.set(e)
            sentinelThread.interrupt()
            closerThread.interrupt()
            log.warn("$name producer run() threw an exception, interrupted other $name threads", e)
        }
        producerThread.start()
        closerThread.start()
        try {
            closerThread.join()
            producerThread.join()
            sentinelThread.join()
        } catch (e: InterruptedException) {
            log.debug("$name was interrupted", e)
        }
        thrown.get()?.run { throw this }
        log.debug("$name is done")
        return Pair(consumer.flush(), producer.finalState())
    }

    /**
     * Calls [collect] repeatedly until:
     * - either the state has reached or exceeded its upper bound,
     * - or there is no more forward progress from one state to the next.
     *
     * It does this lazily.
     */
    fun collectRepeatedly(initialState: S, upperBound: S): Sequence<Pair<Sequence<R>, S>> =
        Sequence {
            object : Iterator<Pair<Sequence<R>, S>> {

                var nextValue: Pair<Sequence<R>, S>? = collect(initialState)

                override fun hasNext(): Boolean = nextValue != null

                override fun next(): Pair<Sequence<R>, S> {
                    val currentValue = nextValue ?: throw NoSuchElementException()
                    val (_, currentState) = currentValue
                    val hasReachedUpperBound = comparator.compare(currentState, upperBound) >= 0
                    if (hasReachedUpperBound) {
                        nextValue = null
                    } else {
                        // Compute the successor output ahead of time for the next iteration.
                        val (successorOutput, successorState) = collect(currentState)
                        // Stop when reaching a fixed point.
                        val hasProgress = comparator.compare(currentState, successorState) < 0
                        nextValue = if (hasProgress) Pair(successorOutput, successorState) else null
                    }
                    return currentValue
                }
            }
        }

    companion object {
        val log: Logger = LoggerFactory.getLogger(ComponentRunner::class.java)
    }
}
