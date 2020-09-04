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

import com.google.common.annotations.VisibleForTesting;
import io.dataline.commons.concurrency.VoidCallable;
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
 * This class is a runnable that given a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class WorkerRunner implements VoidCallable {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRunner.class);

  private final long jobId;
  private final BasicDataSource connectionPool;
  private final SchedulerPersistence persistence;
  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final WorkerRun.Factory workerRunFactory;

  public WorkerRunner(final long jobId,
                      final BasicDataSource connectionPool,
                      final SchedulerPersistence persistence,
                      final Path workspaceRoot,
                      final ProcessBuilderFactory pbf) {
    this(jobId, connectionPool, persistence, workspaceRoot, pbf, WorkerRun::new);
  }

  @VisibleForTesting WorkerRunner(final long jobId,
                                  final BasicDataSource connectionPool,
                                  final SchedulerPersistence persistence,
                                  final Path workspaceRoot,
                                  final ProcessBuilderFactory pbf,
                                  final WorkerRun.Factory workerRunFactory) {
    this.jobId = jobId;
    this.connectionPool = connectionPool;
    this.persistence = persistence;
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.workerRunFactory = workerRunFactory;
  }

  @Override
  public void voidCall() throws IOException {
    final Job job = persistence.getJob(jobId);

    LOGGER.info("job: {} {} {}", job.getId(), job.getScope(), job.getConfig().getConfigType());
    final Path jobRoot = workspaceRoot.resolve(String.valueOf(jobId));

    switch (job.getConfig().getConfigType()) {
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION -> {
        final StandardCheckConnectionInput checkConnectionInput = createCheckConnectionInput(job.getConfig().getCheckConnection());
        workerRunFactory.create(
            jobId,
            jobRoot,
            checkConnectionInput,
            new SingerCheckConnectionWorker(new SingerDiscoverSchemaWorker(job.getConfig().getDiscoverSchema().getDockerImage(), pbf)),
            connectionPool)
            .run();
      }
      case DISCOVER_SCHEMA -> {
        final StandardDiscoverSchemaInput discoverSchemaInput = createDiscoverSchemaInput(job.getConfig().getDiscoverSchema());
        workerRunFactory.create(
            jobId,
            jobRoot,
            discoverSchemaInput,
            new SingerDiscoverSchemaWorker(job.getConfig().getDiscoverSchema().getDockerImage(), pbf),
            connectionPool)
            .run();
      }
      case SYNC -> {
        final StandardSyncInput syncInput = createSyncInput(job.getConfig().getSync());
        final SingerDiscoverSchemaWorker discoverSchemaWorker =
            new SingerDiscoverSchemaWorker(job.getConfig().getSync().getSourceDockerImage(), pbf);
        workerRunFactory.create(
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
      }
      default -> throw new RuntimeException("Unexpected config type: " + job.getConfig().getConfigType());
    }
  }

  private static StandardCheckConnectionInput createCheckConnectionInput(JobCheckConnectionConfig config) {
    return new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardDiscoverSchemaInput createDiscoverSchemaInput(JobDiscoverSchemaConfig config) {
    return new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(config.getConnectionConfiguration());
  }

  private static StandardSyncInput createSyncInput(JobSyncConfig config) {
    return new StandardSyncInput()
        .withSourceConnectionImplementation(config.getSourceConnectionImplementation())
        .withDestinationConnectionImplementation(config.getDestinationConnectionImplementation())
        .withStandardSync(config.getStandardSync());
  }

}
