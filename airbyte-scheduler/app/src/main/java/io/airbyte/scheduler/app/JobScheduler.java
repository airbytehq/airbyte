/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
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
  private final SpecFetcher specFetcher;

  @VisibleForTesting
  JobScheduler(final JobPersistence jobPersistence,
               final ConfigRepository configRepository,
               final BiPredicate<Optional<Job>, StandardSync> scheduleJobPredicate,
               final SyncJobFactory jobFactory,
               final SpecFetcher specFetcher) {
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.scheduleJobPredicate = scheduleJobPredicate;
    this.jobFactory = jobFactory;
    this.specFetcher = specFetcher;
  }

  public JobScheduler(final JobPersistence jobPersistence,
                      final ConfigRepository configRepository,
                      final OAuthConfigSupplier oAuthSupplier,
                      final SpecFetcher specFetcher) {
    this(
        jobPersistence,
        configRepository,
        new ScheduleJobPredicate(Instant::now),
        new DefaultSyncJobFactory(
            new DefaultJobCreator(jobPersistence),
            configRepository,
            oAuthSupplier),
        specFetcher);
  }

  @Override
  public void run() {
    try {
      LOGGER.debug("Running job-scheduler...");

      scheduleSyncJobs();

      LOGGER.debug("Completed Job-Scheduler...");
    } catch (final Throwable e) {
      LOGGER.error("Job Scheduler Error", e);
    }
  }

  private void scheduleSyncJobs() throws IOException {
    int jobsScheduled = 0;
    final var start = System.currentTimeMillis();
    final List<StandardSync> activeConnections = getAllActiveConnections();
    final var queryEnd = System.currentTimeMillis();
    LOGGER.debug("Total active connections: {}", activeConnections.size());
    LOGGER.debug("Time to retrieve all connections: {} ms", queryEnd - start);

    for (final StandardSync connection : activeConnections) {
      final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(connection.getConnectionId());

      if (scheduleJobPredicate.test(previousJobOptional, connection)) {
        final UUID connectionId = connection.getConnectionId();
        jobFactory.create(connectionId, getConnectionSourceSpec(connectionId));
        jobsScheduled++;
        SchedulerApp.PENDING_JOBS.getAndIncrement();
      }
    }
    final var end = System.currentTimeMillis();
    LOGGER.debug("Time taken to schedule jobs: {} ms", end - start);

    if (jobsScheduled > 0) {
      LOGGER.info("Job-Scheduler Summary. Active connections: {}, Jobs scheduled this cycle: {}", activeConnections.size(), jobsScheduled);
    }
  }

  private ConnectorSpecification getConnectionSourceSpec(final UUID connectionId) throws IOException {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);
      final SourceConnection sourceConnection = configRepository.getSourceConnection(standardSync.getSourceId());
      final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
      final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
      return specFetcher.execute(imageName);
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException("Failed to fetch spec for connector");
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
