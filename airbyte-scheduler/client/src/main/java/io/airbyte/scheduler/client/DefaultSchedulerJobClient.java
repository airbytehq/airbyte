/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.ActorDefinitionResourceRequirements;
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
import javax.annotation.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerJobClient implements SchedulerJobClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerJobClient.class);

  private final boolean connectorSpecificResourceDefaultsEnabled;
  private final JobPersistence jobPersistence;
  private final JobCreator jobCreator;

  public DefaultSchedulerJobClient(final boolean connectorSpecificResourceDefaultsEnabled,
                                   final JobPersistence jobPersistence,
                                   final JobCreator jobCreator) {
    this.connectorSpecificResourceDefaultsEnabled = connectorSpecificResourceDefaultsEnabled;
    this.jobPersistence = jobPersistence;
    this.jobCreator = jobCreator;
  }

  @Override
  public Job createOrGetActiveSyncJob(final SourceConnection source,
                                      final DestinationConnection destination,
                                      final StandardSync standardSync,
                                      final String sourceDockerImage,
                                      final String destinationDockerImage,
                                      final List<StandardSyncOperation> standardSyncOperations,
                                      @Nullable final ActorDefinitionResourceRequirements ignorableSourceResourceRequirements,
                                      @Nullable final ActorDefinitionResourceRequirements ignorableDestinationResourceRequirements)
      throws IOException {

    ActorDefinitionResourceRequirements sourceResourceRequirements = ignorableSourceResourceRequirements;
    ActorDefinitionResourceRequirements destinationResourceRequirements = ignorableDestinationResourceRequirements;

    // for OSS users, make it possible to ignore default actor-level resource requirements
    if (!connectorSpecificResourceDefaultsEnabled) {
      sourceResourceRequirements = null;
      destinationResourceRequirements = null;
    }

    final Optional<Long> jobIdOptional = jobCreator.createSyncJob(
        source,
        destination,
        standardSync,
        sourceDockerImage,
        destinationDockerImage,
        standardSyncOperations,
        sourceResourceRequirements,
        destinationResourceRequirements);

    final long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

  @Override
  public Job createOrGetActiveResetConnectionJob(final DestinationConnection destination,
                                                 final StandardSync standardSync,
                                                 final String destinationDockerImage,
                                                 final List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final Optional<Long> jobIdOptional =
        jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage, standardSyncOperations);

    final long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

}
