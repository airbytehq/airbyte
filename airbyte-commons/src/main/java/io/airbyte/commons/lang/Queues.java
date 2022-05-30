/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class Queues {

  /**
   * Exposes the contents a {@link CloseableQueue} as a {@link Stream}. Consuming or closing the
   * stream does NOT close the queue.
   *
   * @param queue queue whose content will be exposed as a stream.
   * @param <T> type provided by the queue
   * @return stream interface on top of the queue.
   */
  public static <T> Stream<T> toStream(final CloseableQueue<T> queue) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        final T record = queue.poll();
        if (record == null) {
          return false;
        }
        action.accept(record);
        return true;
      }

    }, false);
  }

}
