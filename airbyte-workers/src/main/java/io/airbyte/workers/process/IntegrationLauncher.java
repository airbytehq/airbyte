package io.airbyte.workers.process;

import io.airbyte.workers.WorkerException;
import java.nio.file.Path;

public interface IntegrationLauncher {

  ProcessBuilder spec(final Path jobRoot) throws WorkerException;

  ProcessBuilder check(final Path jobRoot, final String configFilename) throws WorkerException;

  ProcessBuilder discover(final Path jobRoot, final String configFilename) throws WorkerException;

  ProcessBuilder read(final Path jobRoot,
                      final String configFilename,
                      final String catalogFilename,
                      final String stateFilename) throws WorkerException;

  default ProcessBuilder read(final Path jobRoot,
                      final String configFilename,
                      final String catalogFilename) throws WorkerException {
    return read(jobRoot, configFilename, catalogFilename, null);
  }

  ProcessBuilder write(final Path jobRoot,
                      final String configFilename,
                      final String catalogFilename) throws WorkerException;
}
