/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.base.Preconditions
import com.google.common.collect.AbstractIterator
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.stream.StreamStatusUtils
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.*
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Composes multiple [AutoCloseableIterator]s. For each internal iterator, after the first time its
 * [Iterator.hasNext] function returns false, the composite iterator will call
 * [AutoCloseableIterator.close] on that internal iterator.
 *
 * [CompositeIterator]s should be closed. Calling [CompositeIterator.close] will attempt to close
 * each internal iterator as well. Thus the close method on each internal iterator should be
 * idempotent as it is will likely be called multiple times.
 *
 * [CompositeIterator.close] gives the guarantee that it will call close on each internal iterator
 * once (even if any of the iterators throw an exception). After it has attempted to close each one
 * once, [CompositeIterator] will rethrow the _first_ exception that it encountered while closing
 * internal iterators. If multiple internal iterators throw exceptions, only the first exception
 * will be rethrown, though the others will be logged.
 *
 * @param <T> type </T>
 */
class CompositeIterator<T>
internal constructor(
    iterators: List<AutoCloseableIterator<T>>,
    airbyteStreamStatusConsumer: Consumer<AirbyteStreamStatusHolder>?
) : AbstractIterator<T>(), AutoCloseableIterator<T> {
    private val airbyteStreamStatusConsumer: Optional<Consumer<AirbyteStreamStatusHolder>>
    private val iterators: List<AutoCloseableIterator<T>>

    private var i: Int
    private val seenIterators: MutableSet<Optional<AirbyteStreamNameNamespacePair>>
    private var hasClosed: Boolean

    init {
        Preconditions.checkNotNull(iterators)

        this.airbyteStreamStatusConsumer = Optional.ofNullable(airbyteStreamStatusConsumer)
        this.iterators = iterators
        this.i = 0
        this.seenIterators = HashSet()
        this.hasClosed = false
    }

    override fun computeNext(): T? {
        assertHasNotClosed()

        if (iterators.isEmpty()) {
            return endOfData()
        }

        // 1. search for an iterator that hasNext.
        // 2. close each iterator we encounter those that do not.
        // 3. if there are none, we are done.
        while (!currentIterator().hasNext()) {
            try {
                currentIterator().close()
                emitStartStreamStatus(currentIterator().airbyteStream)
                StreamStatusUtils.emitCompleteStreamStatus(
                    airbyteStream,
                    airbyteStreamStatusConsumer
                )
            } catch (e: Exception) {
                StreamStatusUtils.emitIncompleteStreamStatus(
                    airbyteStream,
                    airbyteStreamStatusConsumer
                )
                throw RuntimeException(e)
            }

            if (i + 1 < iterators.size) {
                i++
            } else {
                return endOfData()
            }
        }

        try {
            val isFirstRun = emitStartStreamStatus(currentIterator().airbyteStream)
            val next = currentIterator().next()
            if (isFirstRun) {
                StreamStatusUtils.emitRunningStreamStatus(
                    airbyteStream,
                    airbyteStreamStatusConsumer
                )
            }
            return next
        } catch (e: RuntimeException) {
            StreamStatusUtils.emitIncompleteStreamStatus(airbyteStream, airbyteStreamStatusConsumer)
            throw e
        }
    }

    private fun currentIterator(): AutoCloseableIterator<T> {
        return iterators[i]
    }

    private fun emitStartStreamStatus(
        airbyteStream: Optional<AirbyteStreamNameNamespacePair>
    ): Boolean {
        if (airbyteStream!!.isPresent && !seenIterators.contains(airbyteStream)) {
            seenIterators.add(airbyteStream)
            StreamStatusUtils.emitStartStreamStatus(airbyteStream, airbyteStreamStatusConsumer)
            return true
        }
        return false
    }

    @Throws(Exception::class)
    override fun close() {
        hasClosed = true

        val exceptions: MutableList<Exception> = ArrayList()
        for (iterator in iterators) {
            try {
                iterator.close()
            } catch (e: Exception) {
                LOGGER.error("exception while closing", e)
                exceptions.add(e)
            }
        }

        if (!exceptions.isEmpty()) {
            throw exceptions[0]
        }
    }

    override val airbyteStream: Optional<AirbyteStreamNameNamespacePair>
        get() =
            if (currentIterator() is AirbyteStreamAware) {
                AirbyteStreamAware::class.java.cast(currentIterator()).airbyteStream
            } else {
                Optional.empty()
            }

    private fun assertHasNotClosed() {
        Preconditions.checkState(!hasClosed)
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(CompositeIterator::class.java)
    }
}
