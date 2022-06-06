/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DefaultSyncJobFactoryTest {

  @Test
  void createSyncJobFromConnectionId() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID destinationDefinitionId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID destinationId = UUID.randomUUID();
    final UUID operationId = UUID.randomUUID();
    final DefaultJobCreator jobCreator = mock(DefaultJobCreator.class);
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final long jobId = 11L;

    final StandardSyncOperation operation = new StandardSyncOperation().withOperationId(operationId);
    final List<StandardSyncOperation> operations = List.of(operation);
    final StandardSync standardSync = new StandardSync()
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId));

    final SourceConnection sourceConnection = new SourceConnection().withSourceDefinitionId(sourceDefinitionId);
    final DestinationConnection destinationConnection =
        new DestinationConnection().withDestinationDefinitionId(destinationDefinitionId);
    final String srcDockerRepo = "srcrepo";
    final String srcDockerTag = "tag";
    final String srcDockerImage = DockerUtils.getTaggedImageName(srcDockerRepo, srcDockerTag);

    final String dstDockerRepo = "dstrepo";
    final String dstDockerTag = "tag";
    final String dstDockerImage = DockerUtils.getTaggedImageName(dstDockerRepo, dstDockerTag);

    when(configRepository.getStandardSync(connectionId)).thenReturn(standardSync);
    when(configRepository.getSourceConnection(sourceId)).thenReturn(sourceConnection);
    when(configRepository.getDestinationConnection(destinationId)).thenReturn(destinationConnection);
    when(configRepository.getStandardSyncOperation(operationId)).thenReturn(operation);
    when(jobCreator.createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, dstDockerImage, operations, null, null))
        .thenReturn(Optional.of(jobId));
    when(configRepository.getStandardSourceDefinition(sourceDefinitionId))
        .thenReturn(new StandardSourceDefinition().withSourceDefinitionId(sourceDefinitionId).withDockerRepository(srcDockerRepo)
            .withDockerImageTag(srcDockerTag));

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionId))
        .thenReturn(new StandardDestinationDefinition().withDestinationDefinitionId(destinationDefinitionId).withDockerRepository(dstDockerRepo)
            .withDockerImageTag(dstDockerTag));

    final SyncJobFactory factory = new DefaultSyncJobFactory(true, jobCreator, configRepository, mock(OAuthConfigSupplier.class));
    final long actualJobId = factory.create(connectionId);
    assertEquals(jobId, actualJobId);

    verify(jobCreator)
        .createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, dstDockerImage, operations, null, null);
  }

}
