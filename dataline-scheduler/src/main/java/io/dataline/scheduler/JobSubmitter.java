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

import io.dataline.db.DatabaseHelper;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobSubmitter implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final BasicDataSource connectionPool;
  private final SchedulerPersistence persistence;
  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public JobSubmitter(final ExecutorService threadPool,
                      final BasicDataSource connectionPool,
                      final SchedulerPersistence persistence,
                      final Path workspaceRoot,
                      final ProcessBuilderFactory pbf) {
    this.threadPool = threadPool;
    this.connectionPool = connectionPool;
    this.persistence = persistence;
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      Optional<Job> oldestPendingJob = getOldestPendingJob();

      oldestPendingJob.ifPresent(this::submitJob);
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  // todo: DRY this up
  private Optional<Job> getOldestPendingJob() throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        ctx -> {
          Optional<Record> jobEntryOptional =
              ctx
                  .fetch(
                      "SELECT * FROM jobs WHERE CAST(status AS VARCHAR) = 'pending' ORDER BY created_at ASC LIMIT 1")
                  .stream()
                  .findFirst();

          if (jobEntryOptional.isPresent()) {
            Record jobEntry = jobEntryOptional.get();
            Job job = DefaultSchedulerPersistence.getJobFromRecord(jobEntry);
            return Optional.of(job);
          } else {
            return Optional.empty();
          }
        });
  }

  private void submitJob(Job job) {
    threadPool.submit(
        new WorkerRunner(job.getId(), connectionPool, persistence, workspaceRoot, pbf));
  }

}
