/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.collect.Iterators
import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.function.Consumer
import java.util.function.Function
import java.util.function.Supplier
import java.util.stream.Stream

object AutoCloseableIterators {
    /**
     * Coerces a vanilla [Iterator] into a [AutoCloseableIterator] by adding a no op close function.
     *
     * @param iterator iterator to convert
     * @param <T> type
     * @return closeable iterator </T>
     */
    @JvmStatic
    fun <T> fromIterator(iterator: Iterator<T>): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(iterator, VoidCallable.NOOP, null)
    }

    /**
     * Coerces a vanilla [Iterator] into a [AutoCloseableIterator] by adding a no op close function.
     *
     * @param iterator iterator to convert
     * @param <T> type
     * @return closeable iterator </T>
     */
    @JvmStatic
    fun <T> fromIterator(
        iterator: Iterator<T>,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(iterator, VoidCallable.NOOP, airbyteStream)
    }

    /**
     * Coerces a vanilla [Iterator] into a [AutoCloseableIterator]. The provided onClose function
     * will be called at most one time.
     *
     * @param iterator autocloseable iterator to add another close to
     * @param onClose the function that will be called on close
     * @param <T> type
     * @return new autocloseable iterator with the close function appended </T>
     */
    @JvmStatic
    fun <T> fromIterator(
        iterator: Iterator<T>,
        onClose: VoidCallable,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(iterator, onClose, airbyteStream)
    }

    /**
     * Wraps a [Stream] in a [AutoCloseableIterator]. The first time [AutoCloseableIterator.close]
     * is called, [Stream.close] will be called. It will not be called again subsequently.
     *
     * @param stream stream to wrap
     * @param <T> type
     * @return autocloseable iterator </T>
     */
    @JvmStatic
    fun <T> fromStream(
        stream: Stream<T>,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(stream.iterator(), { stream.close() }, airbyteStream)
    }

    /** Consumes entire iterator and collect it into a list. Then it closes the iterator. */
    @Throws(Exception::class)
    @JvmStatic
    fun <T> toListAndClose(iterator: AutoCloseableIterator<T>): List<T> {
        iterator.use {
            return MoreIterators.toList(iterator)
        }
    }

    /**
     * Returns a [AutoCloseableIterator] that will call the provided supplier ONE time when
     * [AutoCloseableIterator.hasNext] is called the first time. The supplier returns a stream that
     * will be exposed as an iterator.
     *
     * @param iteratorSupplier supplier that provides a autocloseable iterator that will be invoked
     * lazily
     * @param <T> type
     * @return autocloseable iterator </T>
     */
    @JvmStatic
    fun <T> lazyIterator(
        iteratorSupplier: Supplier<AutoCloseableIterator<T>>,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return LazyAutoCloseableIterator(iteratorSupplier, airbyteStream)
    }

    /**
     * Append a function to be called on [AutoCloseableIterator.close].
     *
     * @param autoCloseableIterator autocloseable iterator to add another close to
     * @param voidCallable the function that will be called on close
     * @param <T> type
     * @return new autocloseable iterator with the close function appended </T>
     */
    @JvmStatic
    fun <T> appendOnClose(
        autoCloseableIterator: AutoCloseableIterator<T>,
        voidCallable: VoidCallable
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(
            autoCloseableIterator,
            {
                autoCloseableIterator.close()
                voidCallable.call()
            },
            null
        )
    }

    /**
     * Append a function to be called on [AutoCloseableIterator.close].
     *
     * @param autoCloseableIterator autocloseable iterator to add another close to
     * @param voidCallable the function that will be called on close
     * @param <T> type
     * @return new autocloseable iterator with the close function appended </T>
     */
    fun <T> appendOnClose(
        autoCloseableIterator: AutoCloseableIterator<T>,
        voidCallable: VoidCallable,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(
            autoCloseableIterator,
            {
                autoCloseableIterator.close()
                voidCallable.call()
            },
            airbyteStream
        )
    }

    /**
     * Lift and shift of Guava's [Iterators.transform] using the [AutoCloseableIterator] interface.
     *
     * @param fromIterator input autocloseable iterator
     * @param function map function
     * @param <F> input type
     * @param <T> output type
     * @return mapped autocloseable iterator </T></F>
     */
    @JvmStatic
    fun <F, T> transform(
        fromIterator: AutoCloseableIterator<F>,
        function: Function<in F, out T>
    ): AutoCloseableIterator<T> {
        val transformed = Iterators.transform(fromIterator) { function.apply(it) }
        return DefaultAutoCloseableIterator(transformed, fromIterator::close, null)
    }

    /**
     * Lift and shift of Guava's [Iterators.transform] using the [AutoCloseableIterator] interface.
     *
     * @param fromIterator input autocloseable iterator
     * @param function map function
     * @param <F> input type
     * @param <T> output type
     * @return mapped autocloseable iterator </T></F>
     */
    @JvmStatic
    fun <F, T> transform(
        fromIterator: AutoCloseableIterator<F>,
        airbyteStream: AirbyteStreamNameNamespacePair?,
        function: Function<in F, out T>
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(
            Iterators.transform(fromIterator) { t: F -> function.apply(t) },
            { fromIterator.close() },
            airbyteStream
        )
    }

    /**
     * Map over a [AutoCloseableIterator] using a vanilla [Iterator] while retaining all of the
     * Resource behavior of the input [AutoCloseableIterator].
     *
     * @param iteratorCreator function that takes in a autocloseable iterator and uses it to create
     * a vanilla iterator
     * @param autoCloseableIterator input autocloseable iterator
     * @param <T> type
     * @return autocloseable iterator that still has the close functionality of the original input
     * iterator but is transformed by the iterator output by the iteratorCreator </T>
     */
    @JvmStatic
    fun <T> transform(
        iteratorCreator: Function<AutoCloseableIterator<T>, Iterator<T>>,
        autoCloseableIterator: AutoCloseableIterator<T>,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<T> {
        return DefaultAutoCloseableIterator(
            iteratorCreator.apply(autoCloseableIterator),
            { autoCloseableIterator.close() },
            airbyteStream
        )
    }

    @JvmStatic
    fun <T, F> transformIterator(
        iteratorCreator: Function<AutoCloseableIterator<T>, Iterator<F>>,
        autoCloseableIterator: AutoCloseableIterator<T>,
        airbyteStream: AirbyteStreamNameNamespacePair?
    ): AutoCloseableIterator<F> {
        return DefaultAutoCloseableIterator(
            iteratorCreator.apply(autoCloseableIterator),
            { autoCloseableIterator.close() },
            airbyteStream
        )
    }

    @SafeVarargs
    @JvmStatic
    fun <T> concatWithEagerClose(
        airbyteStreamStatusConsumer: Consumer<AirbyteStreamStatusHolder>?,
        vararg iterators: AutoCloseableIterator<T>
    ): CompositeIterator<T> {
        return concatWithEagerClose(java.util.List.of(*iterators), airbyteStreamStatusConsumer)
    }

    @SafeVarargs
    @JvmStatic
    fun <T> concatWithEagerClose(vararg iterators: AutoCloseableIterator<T>): CompositeIterator<T> {
        return concatWithEagerClose(java.util.List.of(*iterators), null)
    }

    /**
     * Creates a [CompositeIterator] that reads from the provided iterators in a serial fashion.
     *
     * @param iterators The list of iterators to be used in a serial fashion.
     * @param airbyteStreamStatusConsumer The stream status consumer used to report stream status
     * during iteration.
     * @return A [CompositeIterator].
     * @param <T> The type of data contained in each iterator. </T>
     */
    @JvmStatic
    fun <T> concatWithEagerClose(
        iterators: List<AutoCloseableIterator<T>>,
        airbyteStreamStatusConsumer: Consumer<AirbyteStreamStatusHolder>?
    ): CompositeIterator<T> {
        return CompositeIterator(iterators, airbyteStreamStatusConsumer)
    }

    @JvmStatic
    fun <T> concatWithEagerClose(iterators: List<AutoCloseableIterator<T>>): CompositeIterator<T> {
        return concatWithEagerClose(iterators, null)
    }
}
