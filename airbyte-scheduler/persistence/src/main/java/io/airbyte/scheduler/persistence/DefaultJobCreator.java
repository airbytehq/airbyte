/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Optional;

public class DefaultJobCreator implements JobCreator {

  private final JobPersistence jobPersistence;

  public DefaultJobCreator(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  @Override
  public Optional<Long> createSyncJob(SourceConnection source,
                                      DestinationConnection destination,
                                      StandardSync standardSync,
                                      String sourceDockerImageName,
                                      String destinationDockerImageName,
                                      List<StandardSyncOperation> standardSyncOperations)
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
        .withResourceRequirements(standardSync.getResourceRequirements());

    jobPersistence.getCurrentState(standardSync.getConnectionId()).ifPresent(jobSyncConfig::withState);

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
  public Optional<Long> createResetConnectionJob(DestinationConnection destination,
                                                 StandardSync standardSync,
                                                 String destinationDockerImage,
                                                 List<StandardSyncOperation> standardSyncOperations)
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
        .withResourceRequirements(standardSync.getResourceRequirements());

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(resetConnectionConfig);
    return jobPersistence.enqueueJob(standardSync.getConnectionId().toString(), jobConfig);
  }

}
