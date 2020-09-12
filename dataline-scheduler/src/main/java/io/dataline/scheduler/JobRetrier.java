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

import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

public class JobRetrier implements Runnable {

  private static final int MAX_RETRIES = 5;
  private static final int RETRY_WAIT_MINUTES = 1;

  private ConfigPersistence configPersistence;
  private final SchedulerPersistence persistence;
  private Supplier<Instant> timeSupplier;

  public JobRetrier(ConfigPersistence configPersistence, SchedulerPersistence schedulerPersistence, Supplier<Instant> timeSupplier) {
    this.configPersistence = configPersistence;
    this.persistence = schedulerPersistence;
    this.timeSupplier = timeSupplier;
  }

  @Override
  public void run() {
    SchedulerUtils.getAllActiveConnections().stream()
        .flatMap(connection -> persistence.listJobs(JobConfig.ConfigType.SYNC, connection, JobStatus.FAILED))
        .filter(job -> {
          // if (job.getAttempts() > MAX_RETRIES) {
          // return false;
          // }

          return isTimeToRetry(job);
        })
        .forEach(job -> persistence.updateStatus(job.getId(), JobStatus.RUNNING));
  }

  private boolean isTimeToRetry(Job job) {
    long lastRun = job.getUpdatedAtInSecond();
    // todo (cgardens) - use exponential backoff instead.
    return lastRun < timeSupplier.get().getEpochSecond() + TimeUnit.MINUTES.toSeconds(RETRY_WAIT_MINUTES);
  }

}
