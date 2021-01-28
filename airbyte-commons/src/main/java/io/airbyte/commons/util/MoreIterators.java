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

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.VoidCallable2;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class MoreIterators {

  public static <T> Iterator<T> of(T... elements) {
    return Arrays.asList(elements).iterator();
  }

  public static <T> List<T> toList(Iterator<T> iterator) {
    final List<T> list = new ArrayList<>();
    while (iterator.hasNext()) {
      list.add(iterator.next());
    }
    return list;
  }

  public static <T> Set<T> toSet(Iterator<T> iterator) {
    final Set<T> set = new HashSet<>();
    while (iterator.hasNext()) {
      set.add(iterator.next());
    }
    return set;
  }

  /**
   * Create an iterator that only executes the given supplier after the first invocation of hasNext.
   * When fully consumed it will close the input stream.
   *
   * @param streamSupplier stream to be supplied lazily
   * @param <T> type
   * @return lazy, auto closing iterator
   */
  public static <T> Iterator<T> streamSupplierToLazyIterator(Supplier<Stream<T>> streamSupplier) {
    return iteratorSupplierToLazyIterator(() -> autoCloseIterator(streamSupplier.get()));
  }

  /**
   * Create an iterator that only executes the given supplier aft the first invocation of hasNext.
   *
   * @param iteratorSupplier iterator to be supplied lazily
   * @param <T> type
   * @return lazy iterator
   */
  public static <T> Iterator<T> iteratorSupplierToLazyIterator(Supplier<Iterator<T>> iteratorSupplier) {
    return new LazyIterator<>(iteratorSupplier);
  }

  private static class LazyIterator<T> extends AbstractIterator<T> implements Iterator<T> {

    private final Supplier<Iterator<T>> iteratorSupplier;

    private boolean hasSupplied;
    private Iterator<T> internalIterator;

    public LazyIterator(Supplier<Iterator<T>> iteratorSupplier) {
      this.iteratorSupplier = iteratorSupplier;
      this.hasSupplied = false;
    }

    @Override
    protected T computeNext() {
      if (!hasSupplied) {
        internalIterator = iteratorSupplier.get();
        hasSupplied = true;
      }

      if (internalIterator.hasNext()) {
        return internalIterator.next();
      } else {
        return endOfData();
      }
    }

  }

  /**
   * Creates an iterator from an iterator. The new iterator when fully consumed will execute the
   * onClose function.
   *
   * @param iterator input iterator
   * @param onClose on close function to be executed when iterator is completely consumed
   * @param <T> type
   * @return auto closing iterator
   */
  public static <T> Iterator<T> autoCloseIterator(Iterator<T> iterator, VoidCallable2 onClose) {
    return new AutoCloseIterator<>(iterator, onClose);
  }

  /**
   * Takes a stream and turns it into an iterator that when fully consumed will close the input
   * stream.
   *
   * @param stream stream to convert
   * @param <T> type
   * @return auto closing iterator
   */
  public static <T> Iterator<T> autoCloseIterator(Stream<T> stream) {
    return new AutoCloseIterator<>(stream.iterator(), stream::close);
  }

  private static class AutoCloseIterator<T> extends AbstractIterator<T> implements Iterator<T> {

    private final Iterator<T> internalIterator;
    private final VoidCallable2 onClose;

    public AutoCloseIterator(Iterator<T> iterator, VoidCallable2 onClose) {
      this.internalIterator = iterator;
      this.onClose = onClose;
    }

    @Override
    protected T computeNext() {
      if (internalIterator.hasNext()) {
        return internalIterator.next();
      } else {
        onClose.voidCall();
        return endOfData();
      }
    }

  }

  public static <T> CloseableIterator<T> toCloseableIterator(Iterator<T> iterator) {
    return new DefaultCloseableIterator<>(iterator, new VoidCallable.NoOp());
  }

  public static <T> Iterator<T> toCloseableIterator(CloseableIterator<T> iterator) {
    return new AutoCloseIterator<>(iterator, () -> {
      try {
        iterator.close();
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  public static class DefaultCloseableIterator<T> extends AbstractIterator<T> implements CloseableIterator<T> {

    private final Iterator<T> iterator;
    private final VoidCallable closeable;

    public DefaultCloseableIterator(Iterator<T> iterator, VoidCallable closeable) {

      this.iterator = iterator;
      this.closeable = closeable;
    }

    @Override
    protected T computeNext() {
      if (iterator.hasNext()) {
        return iterator.next();
      } else {
        return endOfData();
      }
    }

    @Override
    public void close() throws Exception {
      closeable.call();
    }

  }

}
