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

import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.scheduler.WorkerRun;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.wrappers.JobOutputCheckConnectionWorker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CheckConnectionWorkerRunFactory implements WorkerRunFactory<JobCheckConnectionConfig> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CheckConnectionWorkerRunFactory.class);

  @Override
  public WorkerRun create(Path jobRoot, ProcessBuilderFactory pbf, long jobId, int attempt, JobCheckConnectionConfig config) {
    final StandardCheckConnectionInput checkConnectionInput = getCheckConnectionInput(config);

    final IntegrationLauncher launcher = WorkerRunFactoryUtils.createLauncher(jobId, attempt, config.getDockerImage(), pbf);

    return new WorkerRun(
        jobRoot,
        checkConnectionInput,
        new JobOutputCheckConnectionWorker(new DefaultCheckConnectionWorker(launcher)));
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(JobCheckConnectionConfig config) {
    return new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

}
