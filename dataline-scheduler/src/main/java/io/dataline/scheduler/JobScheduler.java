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
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.scheduler.job_factory.DefaultSyncJobFactory;
import io.dataline.scheduler.job_factory.SyncJobFactory;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.function.BiPredicate;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobScheduler implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobScheduler.class);

  private final SchedulerPersistence schedulerPersistence;
  private final ConfigPersistence configPersistence;
  private final BiPredicate<Optional<Job>, StandardSyncSchedule> scheduleJobPredicate;
  private final SyncJobFactory jobFactory;

  @VisibleForTesting
  JobScheduler(SchedulerPersistence schedulerPersistence,
               ConfigPersistence configPersistence,
               BiPredicate<Optional<Job>, StandardSyncSchedule> scheduleJobPredicate,
               SyncJobFactory jobFactory) {
    this.schedulerPersistence = schedulerPersistence;
    this.configPersistence = configPersistence;
    this.scheduleJobPredicate = scheduleJobPredicate;
    this.jobFactory = jobFactory;
  }

  public JobScheduler(SchedulerPersistence schedulerPersistence, ConfigPersistence configPersistence) {
    this(
        schedulerPersistence,
        configPersistence,
        new ScheduleJobPredicate(Instant::now),
        new DefaultSyncJobFactory(schedulerPersistence, configPersistence));
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-scheduler...");

      scheduleSyncJobs();

    } catch (Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleSyncJobs() throws IOException {
    for (StandardSync connection : getAllActiveConnections()) {
      Optional<Job> previousJobOptional = schedulerPersistence.getLastSyncJob(connection.getConnectionId());
      final StandardSyncSchedule standardSyncSchedule = ConfigFetchers.getStandardSyncSchedule(configPersistence, connection.getConnectionId());

      if (scheduleJobPredicate.test(previousJobOptional, standardSyncSchedule)) {
        jobFactory.create(connection.getConnectionId());
      }
    }
  }

  private List<StandardSync> getAllActiveConnections() {
    return ConfigFetchers.getStandardSyncs(configPersistence);
  }

}
