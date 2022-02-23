/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.config.WorkerDestinationConfig;
import java.nio.file.Path;
import java.util.Optional;

public interface Destination<T> extends CheckedConsumer<T, Exception>, AutoCloseable {

  void start(WorkerDestinationConfig destinationConfig, Path jobRoot) throws Exception;

  @Override
  void accept(T message) throws Exception;

  void notifyEndOfStream() throws Exception;

  @Override
  void close() throws Exception;

  void cancel() throws Exception;

  boolean isFinished();

  Optional<T> attemptRead();

}
