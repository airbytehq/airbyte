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

package io.airbyte.scheduler.worker_run_factories;

import io.airbyte.scheduler.WorkerRun;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class BaseWorkerRunAssembly<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseWorkerRunAssembly.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final WorkerRunFactory<T> workerRunFactory;

  public BaseWorkerRunAssembly(final Path workspaceRoot,
                               final ProcessBuilderFactory pbf,
                               final WorkerRunFactory<T> workerRunFactory) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.workerRunFactory = workerRunFactory;
  }

  public WorkerRun create(final long jobId, final int attempt, final T config) {
    final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId)).resolve(String.valueOf(attempt));
    try {
      Files.createDirectories(workspaceRoot);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    return workerRunFactory.create(jobRoot, pbf, jobId, attempt, config);
  }

}
