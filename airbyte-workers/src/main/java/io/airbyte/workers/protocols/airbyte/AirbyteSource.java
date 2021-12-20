/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import java.util.Optional;

/**
 * This interface provides a java interface over all interactions with a Source from the POV of the
 * platform. It encapsulates the full lifecycle of the Source as well as any outputs.
 */
public interface AirbyteSource extends AutoCloseable {

  /**
   * Starts the Source container and opens a connection to STDOUT on that container.
   *
   * @param sourceConfig - contains the arguments that must be passed to the read method of the
   *        Source.
   * @param jobRoot - directory where the job can write data.
   * @throws Exception - throws if there is any failure in startup.
   */
  void start(WorkerSourceConfig sourceConfig, Path jobRoot) throws Exception;

  /**
   * Means no more data will be emitted by the Source. This may be because all data has already been
   * emitted or because the Source container has exited.
   *
   * @return true, if no more data will be emitted. otherwise, false.
   * @throws WorkerException if the Source exited with a non-zero exit code.
   */
  boolean isFinished() throws WorkerException;

  /**
   * Attempts to read an AirbyteMessage from the Source.
   *
   * @return returns an AirbyteMessage is the Source emits one. Otherwise, empty. This method BLOCKS
   *         on waiting for the Source to emit data to STDOUT.
   */
  Optional<AirbyteMessage> attemptRead();

  /**
   * Attempts to shut down the Source's container. Waits for a graceful shutdown, capped by a timeout.
   *
   * @throws Exception - throws if there is any failure in shutdown.
   */
  @Override
  void close() throws Exception;

  /**
   * Attempt to shut down the Source's container quickly.
   *
   * @throws Exception - throws if there is any failure in shutdown.
   */
  void cancel() throws Exception;

}
