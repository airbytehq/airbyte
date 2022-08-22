/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.functional;

import java.util.function.Consumer;
import java.util.function.Function;

public class Consumers {

  /**
   * Adds a function in front of a consumer. The return of the function will be consumed by the
   * original consumer.
   *
   * @param beforeFunction function that will be execute on an item intended for a consumer.
   * @param consumer the consumer that is being preempted.
   * @param <T> type of the consumer.
   * @return consumer that will run the function and then the original consumer on accept.
   */
  public static <T> Consumer<T> wrapConsumer(final Function<T, T> beforeFunction, final Consumer<T> consumer) {
    return (json) -> {
      consumer.accept(beforeFunction.apply(json));
    };
  }

}
