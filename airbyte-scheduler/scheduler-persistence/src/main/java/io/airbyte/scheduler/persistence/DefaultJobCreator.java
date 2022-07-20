/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.State;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import javax.annotation.Nullable;

public class DefaultJobCreator implements JobCreator {

  private final JobPersistence jobPersistence;
  private final ResourceRequirements workerResourceRequirements;
  private final StatePersistence statePersistence;

  public DefaultJobCreator(final JobPersistence jobPersistence,
                           final ResourceRequirements workerResourceRequirements,
                           final StatePersistence statePersistence) {
    this.jobPersistence = jobPersistence;
    this.workerResourceRequirements = workerResourceRequirements;
    this.statePersistence = statePersistence;
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

    getCurrentConnectionState(standardSync.getConnectionId()).ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

  @Override
  public Optional<Long> createResetConnectionJob(final DestinationConnection destination,
                                                 final StandardSync standardSync,
                                                 final String destinationDockerImage,
                                                 final List<StandardSyncOperation> standardSyncOperations,
                                                 final List<StreamDescriptor> streamsToReset)
      throws IOException {
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = standardSync.getCatalog();
    configuredAirbyteCatalog.getStreams().forEach(configuredAirbyteStream -> {
      final StreamDescriptor streamDescriptor = CatalogHelpers.extractDescriptor(configuredAirbyteStream);
      configuredAirbyteStream.setSyncMode(SyncMode.FULL_REFRESH);
      if (streamsToReset.contains(streamDescriptor)) {
        // The Reset Source will emit no record messages for any streams, so setting the destination sync
        // mode to OVERWRITE will empty out this stream in the destination.
        // Note: streams in streamsToReset that are NOT in this configured catalog (i.e. deleted streams)
        // will still have their state reset by the Reset Source, but will not be modified in the
        // destination since they are not present in the catalog that is sent to the destination.
        configuredAirbyteStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
      } else {
        // Set streams that are not being reset to APPEND so that they are not modified in the destination
        configuredAirbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
      }
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
            workerResourceRequirements))
        .withResetSourceConfiguration(new ResetSourceConfiguration().withStreamsToReset(streamsToReset));

    getCurrentConnectionState(standardSync.getConnectionId()).ifPresent(resetConnectionConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(resetConnectionConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

  private Optional<State> getCurrentConnectionState(final UUID connectionId) throws IOException {
    return statePersistence.getCurrentState(connectionId).map(StateMessageHelper::getState);
  }

}
