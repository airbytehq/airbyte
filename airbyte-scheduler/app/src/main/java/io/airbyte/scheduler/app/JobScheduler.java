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

package io.airbyte.scheduler.app;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiPredicate;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobScheduler implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobScheduler.class);

  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final BiPredicate<Optional<Job>, StandardSync> scheduleJobPredicate;
  private final SyncJobFactory jobFactory;

  @VisibleForTesting
  JobScheduler(final JobPersistence jobPersistence,
               final ConfigRepository configRepository,
               final BiPredicate<Optional<Job>, StandardSync> scheduleJobPredicate,
               final SyncJobFactory jobFactory) {
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.scheduleJobPredicate = scheduleJobPredicate;
    this.jobFactory = jobFactory;
  }

  public JobScheduler(final JobPersistence jobPersistence,
                      final ConfigRepository configRepository) {
    this(
        jobPersistence,
        configRepository,
        new ScheduleJobPredicate(Instant::now),
        new DefaultSyncJobFactory(
            new DefaultJobCreator(jobPersistence),
            configRepository,
            new OAuthConfigSupplier(configRepository, false)));
  }

  @Override
  public void run() {
    try {
      LOGGER.debug("Running job-scheduler...");

      scheduleSyncJobs();

      LOGGER.debug("Completed Job-Scheduler...");
    } catch (Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleSyncJobs() throws IOException {
    final AtomicInteger jobsScheduled = new AtomicInteger();
    final List<StandardSync> activeConnections = getAllActiveConnections();

    for (StandardSync connection : activeConnections) {
      final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(connection.getConnectionId());

      if (scheduleJobPredicate.test(previousJobOptional, connection)) {
        jobFactory.create(connection.getConnectionId());
      }
    }
    int jobsScheduledCount = jobsScheduled.get();
    if (jobsScheduledCount > 0) {
      LOGGER.info("Job-Scheduler Summary. Active connections: {}, Jobs scheduler: {}", activeConnections.size(), jobsScheduled.get());
    }
  }

  private List<StandardSync> getAllActiveConnections() {
    try {
      return configRepository.listStandardSyncs()
          .stream()
          .filter(sync -> sync.getStatus() == Status.ACTIVE)
          .collect(Collectors.toList());
    } catch (JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new RuntimeException(e.getMessage(), e);
    }
  }

}
