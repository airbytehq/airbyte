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
import java.util.List;

public interface ProcessFactory {

  /**
   * Creates a ProcessBuilder to run a program in a new Process.
   *
   * @param jobId job Id
   * @param attempt attempt Id
   * @param jobPath Workspace directory to run the process from
   * @param imageName Docker image name to start the process from
   * @param entrypoint If not null, the default entrypoint program of the docker image can be changed
   *        by this argument
   * @param args arguments to pass to the docker image being run in the new process
   * @return the ProcessBuilder object to run the process
   * @throws WorkerException
   */
  Process create(String jobId, int attempt, final Path jobPath, final String imageName, final String entrypoint, final String... args)
      throws WorkerException;

  default Process create(String jobId,
                         int attempt,
                         final Path jobPath,
                         final String imageName,
                         final String entrypoint,
                         final List<String> args)
      throws WorkerException {
    return create(jobId, attempt, jobPath, imageName, entrypoint, args.toArray(new String[0]));
  }

}
