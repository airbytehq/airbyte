/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerJobClient implements SchedulerJobClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerJobClient.class);

  private final JobPersistence jobPersistence;
  private final JobCreator jobCreator;

  public DefaultSchedulerJobClient(JobPersistence jobPersistence, JobCreator jobCreator) {
    this.jobPersistence = jobPersistence;
    this.jobCreator = jobCreator;
  }

  @Override
  public Job createOrGetActiveSyncJob(SourceConnection source,
                                      DestinationConnection destination,
                                      StandardSync standardSync,
                                      String sourceDockerImage,
                                      String destinationDockerImage,
                                      List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final Optional<Long> jobIdOptional = jobCreator.createSyncJob(
        source,
        destination,
        standardSync,
        sourceDockerImage,
        destinationDockerImage,
        standardSyncOperations);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

  @Override
  public Job createOrGetActiveResetConnectionJob(DestinationConnection destination,
                                                 StandardSync standardSync,
                                                 String destinationDockerImage,
                                                 List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final Optional<Long> jobIdOptional =
        jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage, standardSyncOperations);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

}
