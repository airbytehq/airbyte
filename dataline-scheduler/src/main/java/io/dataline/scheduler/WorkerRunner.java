/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import io.dataline.config.JobCheckConnectionConfig;
import io.dataline.config.JobDiscoverSchemaConfig;
import io.dataline.config.JobSyncConfig;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardSyncInput;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.singer.SingerCheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoverSchemaWorker;
import io.dataline.workers.singer.SingerTapFactory;
import io.dataline.workers.singer.SingerTargetFactory;
import java.io.IOException;
import java.nio.file.Path;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class WorkerRunner implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRunner.class);

  private final long jobId;
  private final BasicDataSource connectionPool;
  private final SchedulerPersistence persistence;
  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public WorkerRunner(long jobId,
                      BasicDataSource connectionPool,
                      SchedulerPersistence persistence,
                      Path workspaceRoot,
                      ProcessBuilderFactory pbf) {
    this.jobId = jobId;
    this.connectionPool = connectionPool;
    this.persistence = persistence;
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public void run() {
    final Job job;
    try {
      job = persistence.getJob(jobId);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    LOGGER.info("job: {} {} {}", job.getId(), job.getScope(), job.getConfig().getConfigType());
    final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId));
    LOGGER.info("Job root = {}", jobRoot.toString());
    switch (job.getConfig().getConfigType()) {
      case CHECK_CONNECTION_SOURCE:
      case CHECK_CONNECTION_DESTINATION:
        final StandardCheckConnectionInput checkConnectionInput =
            getCheckConnectionInput(job.getConfig().getCheckConnection());
        LOGGER.info("Starting worker run for {}", jobId);
        new WorkerRun<>(
            jobId,
            jobRoot,
            checkConnectionInput,
            new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(job.getConfig().getDiscoverSchema().getDockerImage(), pbf)),
            connectionPool).run();
        break;
      case DISCOVER_SCHEMA:
        final StandardDiscoverSchemaInput discoverSchemaInput = getDiscoverSchemaInput(job.getConfig().getDiscoverSchema());
        new WorkerRun<>(
            jobId,
            jobRoot,
            discoverSchemaInput,
            new SingerDiscoverSchemaWorker(job.getConfig().getDiscoverSchema().getDockerImage(), pbf),
            connectionPool)
                .run();
        break;
      case SYNC:
        final StandardSyncInput syncInput = getSyncInput(job.getConfig().getSync());
        final SingerDiscoverSchemaWorker discoverSchemaWorker =
            new SingerDiscoverSchemaWorker(job.getConfig().getSync().getSourceDockerImage(), pbf);
        new WorkerRun<>(
            jobId,
            jobRoot,
            syncInput,
            // todo (cgardens) - still locked into only using SingerTaps and Targets. Next step
            // here is to create DefaultTap and DefaultTarget which will be able to
            // interoperate with SingerTap and SingerTarget now that they are split and
            // mediated in DefaultSyncWorker.
            new DefaultSyncWorker(
                new SingerTapFactory(job.getConfig().getSync().getSourceDockerImage(), pbf, discoverSchemaWorker),
                new SingerTargetFactory(job.getConfig().getSync().getDestinationDockerImage(), pbf)),
            connectionPool)
                .run();
        break;
      default:
        throw new RuntimeException("Unexpected config type: " + job.getConfig().getConfigType());
    }
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(JobCheckConnectionConfig config) {
    final StandardCheckConnectionInput checkConnectionInput = new StandardCheckConnectionInput()
        .withConnectionConfiguration(config.getConnectionConfiguration());

    return checkConnectionInput;
  }

  private static StandardDiscoverSchemaInput getDiscoverSchemaInput(JobDiscoverSchemaConfig config) {
    final StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(config.getConnectionConfiguration());

    return discoverSchemaInput;
  }

  private static StandardSyncInput getSyncInput(JobSyncConfig config) {
    final StandardSyncInput syncInput = new StandardSyncInput()
        .withSourceConnectionImplementation(config.getSourceConnectionImplementation())
        .withDestinationConnectionImplementation(config.getDestinationConnectionImplementation())
        .withStandardSync(config.getStandardSync());

    return syncInput;
  }

}
