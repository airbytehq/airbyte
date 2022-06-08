/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import java.nio.file.Path;
import java.util.Optional;

/**
 * This interface provides a java interface over all interactions with a Destination from the POV of
 * the platform. It encapsulates the full lifecycle of the Destination as well as any inputs and
 * outputs.
 */
public interface AirbyteDestination extends CheckedConsumer<AirbyteMessage, Exception>, AutoCloseable {

  /**
   * Starts the Destination container. It instantiates a writer to write to STDIN on that container.
   * It also instantiates a reader to listen on STDOUT.
   *
   * @param destinationConfig - contains the arguments that must be passed to the write method of the
   *        Destination.
   * @param jobRoot - directory where the job can write data.
   * @throws Exception - throws if there is any failure in startup.
   */
  void start(WorkerDestinationConfig destinationConfig, Path jobRoot) throws Exception;

  /**
   * Accepts an AirbyteMessage and writes it to STDIN of the Destination. Blocks if STDIN's buffer is
   * full.
   *
   * @param message message to send to destination.
   * @throws Exception - throws if there is any failure in writing to Destination.
   */
  @Override
  void accept(AirbyteMessage message) throws Exception;

  /**
   * This method is a flush to make sure all data that should be written to the Destination is
   * written. Any messages that have already been accepted
   * ({@link AirbyteDestination#accept(AirbyteMessage)} ()}) will be flushed. Any additional messages
   * sent to accept will not be flushed. In fact, flush should fail if the caller attempts to send it
   * additional messages after calling this method.
   *
   * (Potentially should just rename it to flush)
   *
   * @throws Exception - throws if there is any failure when flushing.
   */
  void notifyEndOfInput() throws Exception;

  /**
   * Means no more data will be emitted by the Destination. This may be because all data has already
   * been emitted or because the Destination container has exited.
   *
   * @return true, if no more data will be emitted. otherwise, false.
   */
  boolean isFinished();

  /**
   * Gets the exit value of the destination process. This should only be called after the destination
   * process has finished.
   *
   * @return exit code of the destination process
   * @throws IllegalStateException if the destination process has not exited
   */
  int getExitValue();

  /**
   * Attempts to read an AirbyteMessage from the Destination.
   *
   * @return returns an AirbyteMessage if the Destination emits one. Otherwise, empty. This method
   *         BLOCKS on waiting for the Destination to emit data to STDOUT.
   */
  Optional<AirbyteMessage> attemptRead();

  /**
   * Attempts to shut down the Destination's container. Waits for a graceful shutdown, capped by a
   * timeout.
   *
   * @throws Exception - throws if there is any failure in shutdown.
   */
  @Override
  void close() throws Exception;

  /**
   * Attempt to shut down the Destination's container quickly.
   *
   * @throws Exception - throws if there is any failure in shutdown.
   */
  void cancel() throws Exception;

}
