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

package io.airbyte.scheduler;

import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverSchemaConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverSchemaInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.SingerCheckConnectionWorker;
import io.airbyte.workers.SingerDiscoverSchemaWorker;
import io.airbyte.workers.SingerSyncWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.process.SingerIntegrationLauncher;
import io.airbyte.workers.protocols.singer.DefaultSingerTap;
import io.airbyte.workers.protocols.singer.DefaultSingerTarget;
import io.airbyte.workers.wrappers.JobOutputCheckConnectionWorker;
import io.airbyte.workers.wrappers.JobOutputDiscoverSchemaWorker;
import io.airbyte.workers.wrappers.JobOutputSyncWorker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class WorkerRunFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRunFactory.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final Creator creator;

  public WorkerRunFactory(final Path workspaceRoot,
                          final ProcessBuilderFactory pbf) {
    this(workspaceRoot, pbf, WorkerRun::new);
  }

  WorkerRunFactory(final Path workspaceRoot,
                   final ProcessBuilderFactory pbf,
                   final Creator creator) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.creator = creator;
  }

  public WorkerRun create(final Job job) {
    final int currentAttempt = job.getAttempts();
    LOGGER.info("job id: {} attempt: {} scope: {} type: {}", job.getId(), currentAttempt, job.getScope(), job.getConfig().getConfigType());

    final Path jobRoot = workspaceRoot.resolve(String.valueOf(job.getId())).resolve(String.valueOf(currentAttempt));
    LOGGER.info("job root: {}", jobRoot);

    switch (job.getConfig().getConfigType()) {
      case CHECK_CONNECTION_SOURCE:
      case CHECK_CONNECTION_DESTINATION:
        final StandardCheckConnectionInput checkConnectionInput = getCheckConnectionInput(job.getConfig().getCheckConnection());
        return creator.create(
            jobRoot,
            checkConnectionInput,
            new JobOutputCheckConnectionWorker(
                new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(
                    new SingerIntegrationLauncher(
                        job.getConfig().getCheckConnection().getDockerImage(),
                        pbf)))));
      case DISCOVER_SCHEMA:
        final StandardDiscoverSchemaInput discoverSchemaInput = getDiscoverSchemaInput(job.getConfig().getDiscoverSchema());
        return creator.create(
            jobRoot,
            discoverSchemaInput,
            new JobOutputDiscoverSchemaWorker(
                new SingerDiscoverSchemaWorker(new SingerIntegrationLauncher(
                    job.getConfig().getDiscoverSchema().getDockerImage(),
                    pbf))));
      case SYNC:
        final StandardSyncInput syncInput = getSyncInput(job.getConfig().getSync());
        final SingerDiscoverSchemaWorker discoverSchemaWorker = new SingerDiscoverSchemaWorker(
            new SingerIntegrationLauncher(
                job.getConfig().getSync().getSourceDockerImage(),
                pbf));
        return creator.create(
            jobRoot,
            syncInput,
            new JobOutputSyncWorker(
                new SingerSyncWorker(
                    new DefaultSingerTap(
                        new SingerIntegrationLauncher(
                            job.getConfig().getSync().getSourceDockerImage(),
                            pbf),
                        discoverSchemaWorker),
                    new DefaultSingerTarget(
                        new SingerIntegrationLauncher(
                            job.getConfig().getSync().getDestinationDockerImage(),
                            pbf)))));
      default:
        throw new RuntimeException("Unexpected config type: " + job.getConfig().getConfigType());
    }

  }

  private static StandardCheckConnectionInput getCheckConnectionInput(JobCheckConnectionConfig config) {
    return new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardDiscoverSchemaInput getDiscoverSchemaInput(JobDiscoverSchemaConfig config) {
    return new StandardDiscoverSchemaInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardSyncInput getSyncInput(JobSyncConfig config) {
    return new StandardSyncInput()
        .withSourceConnectionImplementation(config.getSourceConnectionImplementation())
        .withDestinationConnectionImplementation(config.getDestinationConnectionImplementation())
        .withStandardSync(config.getStandardSync());
  }

  /*
   * This class is here to help with the testing
   */
  @FunctionalInterface
  interface Creator {

    <T> WorkerRun create(Path jobRoot, T input, Worker<T, JobOutput> worker);

  }

}
