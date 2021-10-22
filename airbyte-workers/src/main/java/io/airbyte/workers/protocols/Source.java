/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols;

import io.airbyte.config.WorkerSourceConfig;
import java.nio.file.Path;
import java.util.Optional;

public interface Source<T> extends AutoCloseable {

  void start(WorkerSourceConfig sourceConfig, Path jobRoot) throws Exception;

  boolean isFinished();

  Optional<T> attemptRead();

  @Override
  void close() throws Exception;

  void cancel() throws Exception;

}
