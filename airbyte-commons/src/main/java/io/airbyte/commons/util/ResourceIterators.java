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

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterators;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.concurrency.VoidCallableNoException;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.function.Function;
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
   * Coerces a vanilla {@link Iterator} into a {@link ResourceIterator}. The provided {@param onClose}
   * function will be called at most one time.
   *
   * @param iterator resource iterator to add another close to
   * @param onClose the function that will be called on close
   * @param <T> type
   * @return new resource iterator with the close function appended
   */
  public static <T> ResourceIterator<T> resourceIterator(Iterator<T> iterator, VoidCallableNoException onClose) {
    return new DefaultResourceIterator<>(iterator, onClose::call);
  }

  /**
   * Wraps a {@link Stream} in a {@link ResourceIterator}. The first time
   * {@link ResourceIterator#close()} is called, {@link Stream#close()} will be called. It will not be
   * called again subsequently.
   *
   * @param stream stream to wrap
   * @param <T> type
   * @return resource iterator
   */
  public static <T> ResourceIterator<T> resourceIterator(Stream<T> stream) {
    return new DefaultResourceIterator<>(stream.iterator(), stream::close);
  }

  /**
   * Returns a {@link ResourceIterator} that will call {@link ResourceIterator#close()} at most one
   * time. Either as soon as {@link Iterator#hasNext()} returns false for the first time or when
   * {@link ResourceIterator#close()} is called,
   *
   * @param resourceIterator wrapped resource iterator
   * @param <T> type
   * @return resource iterator
   */
  public static <T> ResourceIterator<T> autoClosingResourceIterator(ResourceIterator<T> resourceIterator) {
    return new AutoCloseIterator<>(resourceIterator);
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

  /**
   * Concatenates {@link ResourceIterator}.
   *
   * @param iterators iterators to concatenate.
   * @param <T> type
   * @return concatenated iterator
   */
  public static <T> ResourceIterator<T> concat(List<ResourceIterator<T>> iterators) {
    return new DefaultResourceIterator<>(Iterators.concat(iterators.iterator()), () -> {
      for (ResourceIterator<T> iterator : iterators) {
        iterator.close();
      }
    });
  }

  public static <T> ResourceIterator<T> concat(ResourceIterator<T> iterator1, ResourceIterator<T> iterator2) {
    return concat(ImmutableList.of(iterator1, iterator2));
  }

}
