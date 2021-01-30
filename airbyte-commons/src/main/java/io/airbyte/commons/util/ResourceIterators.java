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
import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterators;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.concurrency.VoidCallableNoException;
import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class ResourceIterators {

  public static <T> ResourceIterator<T> emptyIterator() {
    return new DefaultResourceIterator<>(Collections.emptyIterator(), VoidCallable.NOOP);
  }

  /**
   * Coerces a vanilla {@link Iterator} into a {@link ResourceIterator} by adding a no op close
   * function.
   *
   * @param iterator iterator to convert
   * @param <T> type
   * @return closeable iterator
   */
  public static <T> ResourceIterator<T> resourceIterator(Iterator<T> iterator) {
    return new DefaultResourceIterator<>(iterator, VoidCallable.NOOP);
  }

  /**
   * Append a function to be called on {@link ResourceIterator#close}.
   *
   * @param resourceIterator resource iterator to add another close to
   * @param voidCallable the function that will be called on close
   * @param <T> type
   * @return new resource iterator with the close function appended
   */
  public static <T> ResourceIterator<T> appendOnClose(ResourceIterator<T> resourceIterator, VoidCallableNoException voidCallable) {
    return new DefaultResourceIterator<>(resourceIterator, () -> {
      resourceIterator.close();
      voidCallable.call();
    });
  }

  /**
   * Lift and shift of Guava's {@link Iterators#transform} using the {@link ResourceIterator}
   * interface.
   *
   * @param fromIterator input resource iterator
   * @param function map function
   * @param <F> input type
   * @param <T> output type
   * @return mapped resource iterator
   */
  public static <F, T> ResourceIterator<T> transform(ResourceIterator<F> fromIterator, Function<? super F, ? extends T> function) {
    return new DefaultResourceIterator<>(Iterators.transform(fromIterator, function::apply), fromIterator::close);
  }

  /**
   * Map over a {@link ResourceIterator} using a vanilla {@link Iterator} while retaining all of the
   * Resource behavior of the input {@link ResourceIterator}.
   *
   * @param iteratorCreator function that takes in a resource iterator and uses it to create a vanilla
   *        iterator
   * @param resourceIterator input resource iterator
   * @param <T> type
   * @return resource iterator that still has the close functionality of the original input iterator
   *         but is transformed by the iterator output by the iteratorCreator
   */
  public static <T> ResourceIterator<T> transform(Function<ResourceIterator<T>, Iterator<T>> iteratorCreator, ResourceIterator<T> resourceIterator) {
    return new DefaultResourceIterator<>(iteratorCreator.apply(resourceIterator), resourceIterator::close);
  }

  @SuppressWarnings("unchecked")
  public static <T> ResourceIterator<T> concat(ResourceIterator<T>... iterators) {
    final AutoCloseIterator<T>[] autoCloseIterators = Arrays
        .stream(iterators)
        .map(iterator -> new AutoCloseIterator<>(iterator, VoidCallableNoException.fromVoidCallable(iterator::close)))
        .toArray(AutoCloseIterator[]::new);

    return new DefaultResourceIterator<>(Iterators.concat(autoCloseIterators), () -> {
      for (ResourceIterator<T> iterator : iterators) {
        iterator.close();
      }
    });
  }

  public static <T> ResourceIterator<T> concat(ResourceIterator<T> iterator1, ResourceIterator<T> iterator2) {
    return concat(ImmutableList.of(iterator1, iterator2));
  }

  /**
   * Concatenates {@link ResourceIterator}. Whenever one of the input iterators is completely consumed
   * the {@link ResourceIterator#close()} will be called immediately. Calling
   * {@link ResourceIterator#close()} on the output iterator will call
   * {@link ResourceIterator#close()} on every input iterator. This means
   * {@link ResourceIterator#close()} can be called multiple times on any of the input iterators.
   *
   * @param iterators iterators to concatenate.
   * @param <T> type
   * @return concatenated iterator
   */
  @SuppressWarnings("unchecked")
  public static <T> ResourceIterator<T> concat(List<ResourceIterator<T>> iterators) {
    final AutoCloseIterator<T>[] autoCloseIterators = iterators
        .stream()
        .map(iterator -> new AutoCloseIterator<>(iterator, VoidCallableNoException.fromVoidCallable(iterator::close)))
        .toArray(AutoCloseIterator[]::new);

    return new DefaultResourceIterator<>(Iterators.concat(autoCloseIterators), () -> {
      for (ResourceIterator<T> iterator : iterators) {
        iterator.close();
      }
    });
  }

  public static <T> ResourceIterator<T> toResourceIterator(Supplier<Stream<T>> streamSupplier) {
    return new LazyResourceIterator<>(() -> {
      final Stream<T> stream = streamSupplier.get();
      // todo problem that we will close this stream multiple times?
      return new DefaultResourceIterator<>(stream.iterator(), stream::close);
    });
  }

  private static class LazyResourceIterator<T> extends AbstractIterator<T> implements ResourceIterator<T> {

    private final Supplier<ResourceIterator<T>> iteratorSupplier;

    private boolean hasSupplied;
    private ResourceIterator<T> internalIterator;

    public LazyResourceIterator(Supplier<ResourceIterator<T>> iteratorSupplier) {
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

    @Override
    public void close() throws Exception {
      internalIterator.close();
    }

  }

  private static class AutoCloseIterator<T> extends AbstractIterator<T> implements Iterator<T> {

    private final Iterator<T> internalIterator;
    private final VoidCallableNoException onClose;

    public AutoCloseIterator(Iterator<T> iterator, VoidCallableNoException onClose) {
      this.internalIterator = iterator;
      this.onClose = onClose;
    }

    @Override
    protected T computeNext() {
      if (internalIterator.hasNext()) {
        return internalIterator.next();
      } else {
        onClose.call();
        return endOfData();
      }
    }

  }

}
