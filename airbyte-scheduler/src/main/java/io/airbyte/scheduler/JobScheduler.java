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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.function.BiPredicate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobScheduler implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobScheduler.class);

  private final SchedulerPersistence schedulerPersistence;
  private final ConfigRepository configRepository;
  private final BiPredicate<Optional<Job>, StandardSyncSchedule> scheduleJobPredicate;
  private final SyncJobFactory jobFactory;

  @VisibleForTesting
  JobScheduler(final SchedulerPersistence schedulerPersistence,
               final ConfigRepository configRepository,
               final BiPredicate<Optional<Job>, StandardSyncSchedule> scheduleJobPredicate,
               final SyncJobFactory jobFactory) {
    this.schedulerPersistence = schedulerPersistence;
    this.configRepository = configRepository;
    this.scheduleJobPredicate = scheduleJobPredicate;
    this.jobFactory = jobFactory;
  }

  public JobScheduler(final SchedulerPersistence schedulerPersistence,
                      final ConfigRepository configRepository) {
    this(
        schedulerPersistence,
        configRepository,
        new ScheduleJobPredicate(Instant::now),
        new DefaultSyncJobFactory(schedulerPersistence, configRepository));
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-scheduler...");

      scheduleSyncJobs();

      LOGGER.info("Completed job-scheduler...");
    } catch (Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleSyncJobs() throws IOException {
    for (StandardSync connection : getAllActiveConnections()) {
      Optional<Job> previousJobOptional = schedulerPersistence.getLastSyncJob(connection.getConnectionId());
      final StandardSyncSchedule standardSyncSchedule = getStandardSyncSchedule(connection);

      if (scheduleJobPredicate.test(previousJobOptional, standardSyncSchedule)) {
        jobFactory.create(connection.getConnectionId());
      }
    }
  }

  private StandardSyncSchedule getStandardSyncSchedule(StandardSync connection) {
    try {
      return configRepository.getStandardSyncSchedule(connection.getConnectionId());
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new RuntimeException(e.getMessage(), e);
    }
  }

  private List<StandardSync> getAllActiveConnections() {
    try {
      return configRepository.listStandardSyncs();
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new RuntimeException(e.getMessage(), e);
    }
  }

}
