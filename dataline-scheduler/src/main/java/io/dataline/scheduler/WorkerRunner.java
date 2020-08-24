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
import io.dataline.config.JobSyncConfig;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardSyncInput;
import io.dataline.workers.DockerCheckConnectionWorker;
import java.io.IOException;
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
      case CHECK_CONNECTION:
        final StandardCheckConnectionInput checkConnectionInput = getCheckConnectionInput(job);
        new WorkerRun<>(
                jobId,
                checkConnectionInput,
                new DockerCheckConnectionWorker(
                    job.getConfig().getCheckConnection().getDockerImage()),
                connectionPool)
            .run();
        break;
      case DISCOVER_SCHEMA:
        throw new RuntimeException("not implemented");
      case SYNC:
        throw new RuntimeException("not implemented");
    }
  }

  private static StandardCheckConnectionInput getCheckConnectionInput(Job job) {
    final JobCheckConnectionConfig checkConnection = job.getConfig().getCheckConnection();
    final StandardCheckConnectionInput checkConnectionInput = new StandardCheckConnectionInput();
    checkConnectionInput.setConnectionConfiguration(checkConnection.getConnectionConfiguration());

    return checkConnectionInput;
  }

  private static StandardDiscoverSchemaInput getDiscoverSchemaInput(Job job) {
    final JobCheckConnectionConfig discoverSchema = job.getConfig().getCheckConnection();
    final StandardDiscoverSchemaInput discoverSchemaInput = new StandardDiscoverSchemaInput();
    discoverSchemaInput.setConnectionConfiguration(discoverSchema.getConnectionConfiguration());

    return discoverSchemaInput;
  }

  private static StandardSyncInput getSyncInput(Job job) {
    final JobSyncConfig sync = job.getConfig().getSync();
    final StandardSyncInput syncInput = new StandardSyncInput();
    syncInput.setSourceConnectionImplementation(sync.getSourceConnectionImplementation());
    syncInput.setDestinationConnectionImplementation(sync.getDestinationConnectionImplementation());
    syncInput.setStandardSync(sync.getStandardSync());

    return syncInput;
  }
}
