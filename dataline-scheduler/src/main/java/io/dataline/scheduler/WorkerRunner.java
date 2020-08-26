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
import io.dataline.workers.singer.SingerCheckConnectionWorker;
import io.dataline.workers.singer.SingerDiscoverSchemaWorker;
import io.dataline.workers.singer.SingerSyncWorker;
import java.io.IOException;
import org.apache.commons.dbcp2.BasicDataSource;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class WorkerRunner implements Runnable {
  private final long jobId;
  private final BasicDataSource connectionPool;
  private final SchedulerPersistence persistence;

  public WorkerRunner(
      long jobId, BasicDataSource connectionPool, SchedulerPersistence persistence) {
    this.jobId = jobId;
    this.connectionPool = connectionPool;
    this.persistence = persistence;
  }

  @Override
  public void run() {
    final Job job;
    try {
      job = persistence.getJob(jobId);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    switch (job.getConfig().getConfigType()) {
      case CHECK_CONNECTION_SOURCE:
      case CHECK_CONNECTION_DESTINATION:
        final StandardCheckConnectionInput checkConnectionInput =
            getCheckConnectionInput(job.getConfig().getCheckConnection());
        new WorkerRun<>(
                jobId,
                checkConnectionInput,
                new SingerCheckConnectionWorker(
                    job.getConfig().getCheckConnection().getDockerImage()),
                connectionPool)
            .run();
        break;
      case DISCOVER_SCHEMA:
        final StandardDiscoverSchemaInput discoverSchemaInput =
            getDiscoverSchemaInput(job.getConfig().getDiscoverSchema());
        new WorkerRun<>(
                jobId,
                discoverSchemaInput,
                new SingerDiscoverSchemaWorker(
                    job.getConfig().getDiscoverSchema().getDockerImage()),
                connectionPool)
            .run();
      case SYNC:
        final StandardSyncInput syncInput = getSyncInput(job.getConfig().getSync());
        new WorkerRun<>(
                jobId,
                syncInput,
                new SingerSyncWorker(
                    job.getConfig().getSync().getSourceDockerImage(),
                    job.getConfig().getSync().getDestinationDockerImage()),
                connectionPool)
            .run();
    }
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(
      JobCheckConnectionConfig config) {
    final StandardCheckConnectionInput checkConnectionInput = new StandardCheckConnectionInput();
    checkConnectionInput.setConnectionConfiguration(config.getConnectionConfiguration());

    return checkConnectionInput;
  }

  private static StandardDiscoverSchemaInput getDiscoverSchemaInput(
      JobDiscoverSchemaConfig config) {
    final StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput();
    discoverSchemaInput.setConnectionConfiguration(config.getConnectionConfiguration());

    return discoverSchemaInput;
  }

  private static StandardSyncInput getSyncInput(JobSyncConfig config) {
    final StandardSyncInput syncInput = new StandardSyncInput();
    syncInput.setSourceConnectionImplementation(config.getSourceConnectionImplementation());
    syncInput.setDestinationConnectionImplementation(
        config.getDestinationConnectionImplementation());
    syncInput.setStandardSync(config.getStandardSync());

    return syncInput;
  }
}
