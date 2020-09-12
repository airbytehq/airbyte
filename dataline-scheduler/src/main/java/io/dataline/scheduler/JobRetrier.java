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

import io.dataline.config.JobConfig;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class JobRetrier implements Runnable {

  private static final int MAX_RETRIES = 5;
  private static final int RETRY_WAIT_MINUTES = 1;

  private ConfigRepository configRepository;
  private final SchedulerPersistence persistence;
  private Supplier<Instant> timeSupplier;

  public JobRetrier(SchedulerPersistence schedulerPersistence, ConfigRepository configRepository, Supplier<Instant> timeSupplier) {
    this.persistence = schedulerPersistence;
    this.configRepository = configRepository;
    this.timeSupplier = timeSupplier;
  }

  @Override
  public void run() {
    SchedulerUtils.getAllActiveConnections(configRepository).stream()
        .flatMap(this::getFailedJobsForConnection)
        .forEach(job -> {
          if (shouldCancel(job)) {
            setSetStatusTo(job, JobStatus.CANCELLED);
            return;
          }

          if (shouldRetry(job)) {
            setSetStatusTo(job, JobStatus.PENDING);
          }
        });
  }

  private Stream<Job> getFailedJobsForConnection(StandardSync connection) {
    try {
      return persistence.listJobs(JobConfig.ConfigType.SYNC, connection.getConnectionId().toString(), JobStatus.FAILED).stream();
    } catch (IOException e) {
      throw new RuntimeException("failed to fetch jobs for connection: " + connection.getConnectionId(), e);
    }
  }

  private boolean shouldCancel(Job job) {
    return job.getAttempts() > MAX_RETRIES;
  }

  private boolean shouldRetry(Job job) {
    long lastRun = job.getUpdatedAtInSecond();
    // todo (cgardens) - use exponential backoff.
    return lastRun < timeSupplier.get().getEpochSecond() + TimeUnit.MINUTES.toSeconds(RETRY_WAIT_MINUTES);
  }

  private void setSetStatusTo(Job job, JobStatus status) {
    try {
      persistence.updateStatus(job.getId(), status);
    } catch (IOException e) {
      throw new RuntimeException("failed to update status for job " + job.getId(), e);
    }
  }

}
