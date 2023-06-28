/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import com.google.common.collect.Iterators;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.Iterator;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class AutoCloseableIterators {

  /**
   * Coerces a vanilla {@link Iterator} into a {@link AutoCloseableIterator} by adding a no op close
   * function.
   *
   * @param iterator iterator to convert
   * @param <T> type
   * @return closeable iterator
   */
  public static <T> AutoCloseableIterator<T> fromIterator(final Iterator<T> iterator) {
    return new DefaultAutoCloseableIterator<>(iterator, VoidCallable.NOOP, null);
  }

  /**
   * Coerces a vanilla {@link Iterator} into a {@link AutoCloseableIterator} by adding a no op close
   * function.
   *
   * @param iterator iterator to convert
   * @param <T> type
   * @return closeable iterator
   */
  public static <T> AutoCloseableIterator<T> fromIterator(final Iterator<T> iterator, final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<>(iterator, VoidCallable.NOOP, airbyteStream);
  }

  /**
   * Coerces a vanilla {@link Iterator} into a {@link AutoCloseableIterator}. The provided onClose
   * function will be called at most one time.
   *
   * @param iterator autocloseable iterator to add another close to
   * @param onClose the function that will be called on close
   * @param <T> type
   * @return new autocloseable iterator with the close function appended
   */
  public static <T> AutoCloseableIterator<T> fromIterator(final Iterator<T> iterator,
                                                          final VoidCallable onClose,
                                                          final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<>(iterator, onClose::call, airbyteStream);
  }

  /**
   * Wraps a {@link Stream} in a {@link AutoCloseableIterator}. The first time
   * {@link AutoCloseableIterator#close()} is called, {@link Stream#close()} will be called. It will
   * not be called again subsequently.
   *
   * @param stream stream to wrap
   * @param <T> type
   * @return autocloseable iterator
   */
  public static <T> AutoCloseableIterator<T> fromStream(final Stream<T> stream, final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<>(stream.iterator(), stream::close, airbyteStream);
  }

  /**
   * Consumes entire iterator and collect it into a list. Then it closes the iterator.
   */
  public static <T> List<T> toListAndClose(final AutoCloseableIterator<T> iterator) throws Exception {
    try (iterator) {
      return MoreIterators.toList(iterator);
    }
  }

  /**
   * Returns a {@link AutoCloseableIterator} that will call the provided supplier ONE time when
   * {@link AutoCloseableIterator#hasNext()} is called the first time. The supplier returns a stream
   * that will be exposed as an iterator.
   *
   * @param iteratorSupplier supplier that provides a autocloseable iterator that will be invoked
   *        lazily
   * @param <T> type
   * @return autocloseable iterator
   */
  public static <T> AutoCloseableIterator<T> lazyIterator(final Supplier<AutoCloseableIterator<T>> iteratorSupplier,
                                                          final AirbyteStreamNameNamespacePair airbyteStream) {
    return new LazyAutoCloseableIterator<>(iteratorSupplier, airbyteStream);
  }

  /**
   * Append a function to be called on {@link AutoCloseableIterator#close}.
   *
   * @param autoCloseableIterator autocloseable iterator to add another close to
   * @param voidCallable the function that will be called on close
   * @param <T> type
   * @return new autocloseable iterator with the close function appended
   */
  public static <T> AutoCloseableIterator<T> appendOnClose(final AutoCloseableIterator<T> autoCloseableIterator, final VoidCallable voidCallable) {
    return new DefaultAutoCloseableIterator<>(autoCloseableIterator, () -> {
      autoCloseableIterator.close();
      voidCallable.call();
    }, null);
  }

  /**
   * Append a function to be called on {@link AutoCloseableIterator#close}.
   *
   * @param autoCloseableIterator autocloseable iterator to add another close to
   * @param voidCallable the function that will be called on close
   * @param <T> type
   * @return new autocloseable iterator with the close function appended
   */
  public static <T> AutoCloseableIterator<T> appendOnClose(final AutoCloseableIterator<T> autoCloseableIterator,
                                                           final VoidCallable voidCallable,
                                                           final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<>(autoCloseableIterator, () -> {
      autoCloseableIterator.close();
      voidCallable.call();
    },
        airbyteStream);
  }

  /**
   * Lift and shift of Guava's {@link Iterators#transform} using the {@link AutoCloseableIterator}
   * interface.
   *
   * @param fromIterator input autocloseable iterator
   * @param function map function
   * @param <F> input type
   * @param <T> output type
   * @return mapped autocloseable iterator
   */
  public static <F, T> AutoCloseableIterator<T> transform(final AutoCloseableIterator<F> fromIterator,
                                                          final Function<? super F, ? extends T> function) {
    return new DefaultAutoCloseableIterator<>(Iterators.transform(fromIterator, function::apply), fromIterator::close, null);
  }

  /**
   * Lift and shift of Guava's {@link Iterators#transform} using the {@link AutoCloseableIterator}
   * interface.
   *
   * @param fromIterator input autocloseable iterator
   * @param function map function
   * @param <F> input type
   * @param <T> output type
   * @return mapped autocloseable iterator
   */
  public static <F, T> AutoCloseableIterator<T> transform(final AutoCloseableIterator<F> fromIterator,
                                                          final AirbyteStreamNameNamespacePair airbyteStream,
                                                          final Function<? super F, ? extends T> function) {
    return new DefaultAutoCloseableIterator<>(Iterators.transform(fromIterator, function::apply), fromIterator::close, airbyteStream);
  }

  /**
   * Map over a {@link AutoCloseableIterator} using a vanilla {@link Iterator} while retaining all of
   * the Resource behavior of the input {@link AutoCloseableIterator}.
   *
   * @param iteratorCreator function that takes in a autocloseable iterator and uses it to create a
   *        vanilla iterator
   * @param autoCloseableIterator input autocloseable iterator
   * @param <T> type
   * @return autocloseable iterator that still has the close functionality of the original input
   *         iterator but is transformed by the iterator output by the iteratorCreator
   */
  public static <T> AutoCloseableIterator<T> transform(final Function<AutoCloseableIterator<T>, Iterator<T>> iteratorCreator,
                                                       final AutoCloseableIterator<T> autoCloseableIterator,
                                                       final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<>(iteratorCreator.apply(autoCloseableIterator), autoCloseableIterator::close, airbyteStream);
  }

  public static <T, F> AutoCloseableIterator<F> transformIterator(final Function<AutoCloseableIterator<T>, Iterator<F>> iteratorCreator,
                                                                  final AutoCloseableIterator<T> autoCloseableIterator,
                                                                  final AirbyteStreamNameNamespacePair airbyteStream) {
    return new DefaultAutoCloseableIterator<F>(iteratorCreator.apply(autoCloseableIterator), autoCloseableIterator::close, airbyteStream);
  }

  @SafeVarargs
  public static <T> CompositeIterator<T> concatWithEagerClose(final Consumer<AirbyteStreamStatusHolder> airbyteStreamStatusConsumer,
                                                              final AutoCloseableIterator<T>... iterators) {
    return concatWithEagerClose(List.of(iterators), airbyteStreamStatusConsumer);
  }

  @SafeVarargs
  public static <T> CompositeIterator<T> concatWithEagerClose(final AutoCloseableIterator<T>... iterators) {
    return concatWithEagerClose(List.of(iterators), null);
  }

  public static <T> CompositeIterator<T> concatWithEagerClose(final List<AutoCloseableIterator<T>> iterators,
                                                              final Consumer<AirbyteStreamStatusHolder> airbyteStreamStatusConsumer) {
    return new CompositeIterator<>(iterators, airbyteStreamStatusConsumer);
  }

  public static <T> CompositeIterator<T> concatWithEagerClose(final List<AutoCloseableIterator<T>> iterators) {
    return concatWithEagerClose(iterators, null);
  }

}
