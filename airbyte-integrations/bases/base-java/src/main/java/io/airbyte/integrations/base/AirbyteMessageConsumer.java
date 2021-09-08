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

package io.airbyte.integrations.base;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.protocol.models.AirbyteMessage;

/**
 * Interface for the destination's consumption of incoming records wrapped in an
 * {@link io.airbyte.protocol.models.AirbyteMessage}.
 *
 * This is via the accept method, which commonly handles parsing, validation, batching and writing
 * of the transformed data to the final destination i.e. the technical system data is being written
 * to.
 *
 * Lifecycle:
 * <li>1. Instantiate consumer.</li>
 * <li>2. start() to initialize any resources that need to be created BEFORE the consumer consumes
 * any messages.</li>
 * <li>3. Consumes ALL records via {@link AirbyteMessageConsumer#accept(AirbyteMessage)}</li>
 * <li>4. Always (on success or failure) finalize by calling
 * {@link AirbyteMessageConsumer#close()}</li>
 *
 * We encourage implementing this interface using the {@link FailureTrackingAirbyteMessageConsumer}
 * class.
 */
public interface AirbyteMessageConsumer extends CheckedConsumer<AirbyteMessage, Exception>, AutoCloseable {

  void start() throws Exception;

  @Override
  void accept(AirbyteMessage message) throws Exception;

  @Override
  void close() throws Exception;

  /**
   * Append a function to be called on {@link AirbyteMessageConsumer#close}.
   */
  static AirbyteMessageConsumer appendOnClose(final AirbyteMessageConsumer consumer, final VoidCallable voidCallable) {
    return new AirbyteMessageConsumer() {

      @Override
      public void start() throws Exception {
        consumer.start();
      }

      @Override
      public void accept(final AirbyteMessage message) throws Exception {
        consumer.accept(message);
      }

      @Override
      public void close() throws Exception {
        consumer.close();
        voidCallable.call();
      }

    };
  }

}
