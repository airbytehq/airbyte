/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.app.worker_run.TemporalWorkerRunFactory;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalClient;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
@AllArgsConstructor
public class NewJobScheduler implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobScheduler.class);

  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final SyncJobFactory jobFactory;
  private final TemporalClient temporalClient;
  private final Path workspaceRoot;
  private final String airbyteVersionOrWarnings;

  public NewJobScheduler(final JobPersistence jobPersistence,
                         final ConfigRepository configRepository,
                         final TrackingClient trackingClient,
                         final TemporalClient temporalClient,
                         final Path workspaceRoot,
                         final String airbyteVersionOrWarnings) {
    this(
        jobPersistence,
        configRepository,
        new DefaultSyncJobFactory(
            new DefaultJobCreator(jobPersistence, configRepository),
            configRepository,
            new OAuthConfigSupplier(configRepository, trackingClient)),
        temporalClient,
        workspaceRoot,
        airbyteVersionOrWarnings);
  }

  @Override
  public void run() {
    try {
      LOGGER.debug("Running new job-scheduler... _________________");

      scheduleNewConnections();

      LOGGER.debug("Completed new Job-Scheduler... _________________");
    } catch (final Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleNewConnections() throws IOException {
    int jobsScheduled = 0;
    final var start = System.currentTimeMillis();
    final List<StandardSync> activeConnections = getAllActiveConnections();
    final var queryEnd = System.currentTimeMillis();
    LOGGER.debug("Total active connections: {}", activeConnections.size());
    LOGGER.debug("Time to retrieve all connections: {} ms", queryEnd - start);

    final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(temporalClient, workspaceRoot, airbyteVersionOrWarnings);

    for (final StandardSync connection : activeConnections) {
      final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(connection.getConnectionId());

      if (previousJobOptional.isEmpty()) {
        // TODO: return a Job in order to avoid fetching it later on.
        final long jobId = jobFactory.create(connection.getConnectionId());
        jobsScheduled++;
        SchedulerApp.PENDING_JOBS.getAndIncrement();
        final Job createdJob = jobPersistence.getJob(jobId);
        temporalWorkerRunFactory.create(createdJob);
      }
    }
    final var end = System.currentTimeMillis();
    LOGGER.debug("Time taken to schedule jobs: {} ms", end - start);

    if (jobsScheduled > 0) {
      LOGGER.info("Job-Scheduler Summary. Active connections: {}, Jobs scheduled this cycle: {}", activeConnections.size(), jobsScheduled);
    }
  }

  private List<StandardSync> getAllActiveConnections() {
    try {
      return configRepository.listStandardSyncs()
          .stream()
          .filter(sync -> sync.getStatus() == Status.ACTIVE)
          .collect(Collectors.toList());
    } catch (final JsonValidationException | IOException | ConfigNotFoundException e) {
      throw new RuntimeException(e.getMessage(), e);
    }
  }

}
