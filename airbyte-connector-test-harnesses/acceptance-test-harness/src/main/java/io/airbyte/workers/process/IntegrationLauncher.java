/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.airbyte.workers.exception.TestHarnessException;
import java.nio.file.Path;
import java.util.Map;

/**
 * This interface provides an abstraction for launching a container that implements the Airbyte
 * Protocol. Such containers implement each method that is defined in the Protocol. This class,
 * provides java methods to invoke the methods on these containers.
 *
 * Each method takes in a jobRoot that is a directory where the worker that runs the method can use
 * as temporary file system storage.
 */
public interface IntegrationLauncher {

  Process spec(final Path jobRoot) throws TestHarnessException;

  Process check(final Path jobRoot, final String configFilename, final String configContents) throws TestHarnessException;

  Process discover(final Path jobRoot, final String configFilename, final String configContents) throws TestHarnessException;

  Process read(final Path jobRoot,
               final String configFilename,
               final String configContents,
               final String catalogFilename,
               final String catalogContents,
               final String stateFilename,
               final String stateContents)
      throws TestHarnessException;

  default Process read(final Path jobRoot,
                       final String configFilename,
                       final String configContents,
                       final String catalogFilename,
                       final String catalogContents)
      throws TestHarnessException {
    return read(jobRoot, configFilename, configContents, catalogFilename, catalogContents, null, null);
  }

  Process write(final Path jobRoot,
                final String configFilename,
                final String configContents,
                final String catalogFilename,
                final String catalogContents,
                final Map<String, String> additionalEnvironmentVariables)
      throws TestHarnessException;

}
