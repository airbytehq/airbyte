/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.airbyte.workers.WorkerException;
import java.nio.file.Path;

public interface IntegrationLauncher {

  Process spec(final Path jobRoot) throws WorkerException;

  Process check(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException;

  Process discover(final Path jobRoot, final String configFilename, final String configContents) throws WorkerException;

  Process read(final Path jobRoot,
               final String configFilename,
               final String configContents,
               final String catalogFilename,
               final String catalogContents,
               final String stateFilename,
               final String stateContents)
      throws WorkerException;

  default Process read(final Path jobRoot,
                       final String configFilename,
                       final String configContents,
                       final String catalogFilename,
                       final String catalogContents)
      throws WorkerException {
    return read(jobRoot, configFilename, configContents, catalogFilename, catalogContents, null, null);
  }

  Process write(final Path jobRoot,
                final String configFilename,
                final String configContents,
                final String catalogFilename,
                final String catalogContents)
      throws WorkerException;

}
