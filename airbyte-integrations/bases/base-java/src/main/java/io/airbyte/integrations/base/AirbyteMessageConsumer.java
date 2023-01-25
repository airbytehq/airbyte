/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;

/**
 * Interface for the destination's consumption of incoming records wrapped in an
 * {@link io.airbyte.protocol.models.v0.AirbyteMessage}.
 *
 * This is via the accept method, which commonly handles parsing, validation, batching and writing
 * of the transformed data to the final destination i.e. the technical system data is being written
 * to.
 *
 * Lifecycle:
 * <ul>
 * <li>1. Instantiate consumer.</li>
 * <li>2. start() to initialize any resources that need to be created BEFORE the consumer consumes
 * any messages.</li>
 * <li>3. Consumes ALL records via {@link AirbyteMessageConsumer#accept(AirbyteMessage)}</li>
 * <li>4. Always (on success or failure) finalize by calling
 * {@link AirbyteMessageConsumer#close()}</li>
 * </ul>
 * We encourage implementing this interface using the {@link FailureTrackingAirbyteMessageConsumer}
 * class.
 */
public interface AirbyteMessageConsumer extends CheckedConsumer<AirbyteMessage, Exception>, AutoCloseable {

  void start() throws Exception;

  /**
   * Consumes all {@link AirbyteMessage}s
   *
   * @param message {@link AirbyteMessage} to be processed
   * @throws Exception
   */
  @Override
  void accept(AirbyteMessage message) throws Exception;

  /**
   * Executes at the end of consumption of all incoming streamed data regardless of success or failure
   *
   * @throws Exception
   */
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
