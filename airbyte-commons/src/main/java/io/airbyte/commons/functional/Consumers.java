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
  public static <T> Consumer<T> wrapConsumer(Function<T, T> beforeFunction, Consumer<T> consumer) {
    return (json) -> {
      consumer.accept(beforeFunction.apply(json));
    };
  }

}
