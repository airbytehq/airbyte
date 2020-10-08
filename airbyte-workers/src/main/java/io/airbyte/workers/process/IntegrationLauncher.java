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
                      final String stateFilename)
      throws WorkerException;

  default ProcessBuilder read(final Path jobRoot,
                              final String configFilename,
                              final String catalogFilename)
      throws WorkerException {
    return read(jobRoot, configFilename, catalogFilename, null);
  }

  ProcessBuilder write(final Path jobRoot,
                       final String configFilename,
                       final String catalogFilename)
      throws WorkerException;

  // TODO: this version should be removed once we've moved away from singer protocol
  default ProcessBuilder write(final Path jobRoot,
                               final String configFilename)
      throws WorkerException {
    return write(jobRoot, configFilename, null);
  }

}
