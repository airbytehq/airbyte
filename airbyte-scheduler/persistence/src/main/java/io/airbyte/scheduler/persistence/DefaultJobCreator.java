/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import javax.annotation.Nullable;

public class DefaultJobCreator implements JobCreator {

  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final ResourceRequirements workerResourceRequirements;

  public DefaultJobCreator(final JobPersistence jobPersistence,
                           final ConfigRepository configRepository,
                           final ResourceRequirements workerResourceRequirements) {
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.workerResourceRequirements = workerResourceRequirements;
  }

  @Override
  public Optional<Long> createSyncJob(final SourceConnection source,
                                      final DestinationConnection destination,
                                      final StandardSync standardSync,
                                      final String sourceDockerImageName,
                                      final String destinationDockerImageName,
                                      final List<StandardSyncOperation> standardSyncOperations,
                                      @Nullable final ActorDefinitionResourceRequirements sourceResourceReqs,
                                      @Nullable final ActorDefinitionResourceRequirements destinationResourceReqs)
      throws IOException {
    // reusing this isn't going to quite work.
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(standardSync.getNamespaceDefinition())
        .withNamespaceFormat(standardSync.getNamespaceFormat())
        .withPrefix(standardSync.getPrefix())
        .withSourceDockerImage(sourceDockerImageName)
        .withSourceConfiguration(source.getConfiguration())
        .withDestinationDockerImage(destinationDockerImageName)
        .withDestinationConfiguration(destination.getConfiguration())
        .withOperationSequence(standardSyncOperations)
        .withConfiguredAirbyteCatalog(standardSync.getCatalog())
        .withState(null)
        .withResourceRequirements(ResourceRequirementsUtils.getResourceRequirements(
            standardSync.getResourceRequirements(),
            workerResourceRequirements))
        .withSourceResourceRequirements(ResourceRequirementsUtils.getResourceRequirements(
            standardSync.getResourceRequirements(),
            sourceResourceReqs,
            workerResourceRequirements,
            JobType.SYNC))
        .withDestinationResourceRequirements(ResourceRequirementsUtils.getResourceRequirements(
            standardSync.getResourceRequirements(),
            destinationResourceReqs,
            workerResourceRequirements,
            JobType.SYNC));

    configRepository.getConnectionState(standardSync.getConnectionId()).ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

  // Strategy:
  // 1. Set all streams to full refresh - overwrite.
  // 2. Create a job where the source emits no records.
  // 3. Run a sync from the empty source to the destination. This will overwrite all data for each
  // stream in the destination.
  // 4. The Empty source emits no state message, so state will start at null (i.e. start from the
  // beginning on the next sync).
  @Override
  public Optional<Long> createResetConnectionJob(final DestinationConnection destination,
                                                 final StandardSync standardSync,
                                                 final String destinationDockerImage,
                                                 final List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = standardSync.getCatalog();
    configuredAirbyteCatalog.getStreams().forEach(configuredAirbyteStream -> {
      configuredAirbyteStream.setSyncMode(SyncMode.FULL_REFRESH);
      configuredAirbyteStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
    });
    final JobResetConnectionConfig resetConnectionConfig = new JobResetConnectionConfig()
        .withNamespaceDefinition(standardSync.getNamespaceDefinition())
        .withNamespaceFormat(standardSync.getNamespaceFormat())
        .withPrefix(standardSync.getPrefix())
        .withDestinationDockerImage(destinationDockerImage)
        .withDestinationConfiguration(destination.getConfiguration())
        .withOperationSequence(standardSyncOperations)
        .withConfiguredAirbyteCatalog(configuredAirbyteCatalog)
        .withResourceRequirements(ResourceRequirementsUtils.getResourceRequirements(
            standardSync.getResourceRequirements(),
            workerResourceRequirements));

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(resetConnectionConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

}
