/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;

/**
 * Interface for the destination's consumption of incoming messages as strings. This interface is
 * backwards compatible with {@link AirbyteMessageConsumer}.
 * <p>
 * This is via the accept method, which commonly handles parsing, validation, batching and writing
 * of the transformed data to the final destination i.e. the technical system data is being written
 * to.
 * <p>
 * Lifecycle:
 * <ul>
 * <li>1. Instantiate consumer.</li>
 * <li>2. start() to initialize any resources that need to be created BEFORE the consumer consumes
 * any messages.</li>
 * <li>3. Consumes ALL records via
 * {@link SerializedAirbyteMessageConsumer#accept(String, Integer)}</li>
 * <li>4. Always (on success or failure) finalize by calling
 * {@link SerializedAirbyteMessageConsumer#close()}</li>
 * </ul>
 */
public interface SerializedAirbyteMessageConsumer extends CheckedBiConsumer<String, Integer, Exception>, AutoCloseable {

  /**
   * Initialize anything needed for the consumer. Must be called before accept.
   *
   * @throws Exception exception
   */
  void start() throws Exception;

  /**
   * Consumes all {@link AirbyteMessage}s
   *
   * @param message {@link AirbyteMessage} as a string
   * @param sizeInBytes size of that string in bytes
   * @throws Exception exception
   */
  @Override
  void accept(String message, Integer sizeInBytes) throws Exception;

  /**
   * Executes at the end of consumption of all incoming streamed data regardless of success or failure
   *
   * @throws Exception exception
   */
  @Override
  void close() throws Exception;

  /**
   * Append a function to be called on {@link SerializedAirbyteMessageConsumer#close}.
   */
  static SerializedAirbyteMessageConsumer appendOnClose(final SerializedAirbyteMessageConsumer consumer, final VoidCallable voidCallable) {
    return new SerializedAirbyteMessageConsumer() {

      @Override
      public void start() throws Exception {
        consumer.start();
      }

      @Override
      public void accept(final String message, final Integer sizeInBytes) throws Exception {
        consumer.accept(message, sizeInBytes);
      }

      @Override
      public void close() throws Exception {
        consumer.close();
        voidCallable.call();
      }

    };
  }

}
