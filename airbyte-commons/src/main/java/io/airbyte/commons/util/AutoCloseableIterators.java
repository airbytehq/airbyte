/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.commons.util;

import com.google.common.collect.Iterators;
import io.airbyte.commons.concurrency.VoidCallable;
import java.util.Iterator;
import java.util.List;
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
  public static <T> AutoCloseableIterator<T> fromIterator(Iterator<T> iterator) {
    return new DefaultAutoCloseableIterator<>(iterator, VoidCallable.NOOP);
  }

  /**
   * Coerces a vanilla {@link Iterator} into a {@link AutoCloseableIterator}. The provided
   * {@param onClose} function will be called at most one time.
   *
   * @param iterator autocloseable iterator to add another close to
   * @param onClose the function that will be called on close
   * @param <T> type
   * @return new autocloseable iterator with the close function appended
   */
  public static <T> AutoCloseableIterator<T> fromIterator(Iterator<T> iterator, VoidCallable onClose) {
    return new DefaultAutoCloseableIterator<>(iterator, onClose::call);
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
  public static <T> AutoCloseableIterator<T> fromStream(Stream<T> stream) {
    return new DefaultAutoCloseableIterator<>(stream.iterator(), stream::close);
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
  public static <T> AutoCloseableIterator<T> lazyIterator(Supplier<AutoCloseableIterator<T>> iteratorSupplier) {
    return new LazyAutoCloseableIterator<>(iteratorSupplier);
  }

  /**
   * Append a function to be called on {@link AutoCloseableIterator#close}.
   *
   * @param autoCloseableIterator autocloseable iterator to add another close to
   * @param voidCallable the function that will be called on close
   * @param <T> type
   * @return new autocloseable iterator with the close function appended
   */
  public static <T> AutoCloseableIterator<T> appendOnClose(AutoCloseableIterator<T> autoCloseableIterator, VoidCallable voidCallable) {
    return new DefaultAutoCloseableIterator<>(autoCloseableIterator, () -> {
      autoCloseableIterator.close();
      voidCallable.call();
    });
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
  public static <F, T> AutoCloseableIterator<T> transform(AutoCloseableIterator<F> fromIterator, Function<? super F, ? extends T> function) {
    return new DefaultAutoCloseableIterator<>(Iterators.transform(fromIterator, function::apply), fromIterator::close);
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
  public static <T> AutoCloseableIterator<T> transform(Function<AutoCloseableIterator<T>, Iterator<T>> iteratorCreator,
                                                       AutoCloseableIterator<T> autoCloseableIterator) {
    return new DefaultAutoCloseableIterator<>(iteratorCreator.apply(autoCloseableIterator), autoCloseableIterator::close);
  }

  public static <T> CompositeIterator<T> concatWithEagerClose(List<AutoCloseableIterator<T>> iterators) {
    return new CompositeIterator<>(iterators);
  }

}
