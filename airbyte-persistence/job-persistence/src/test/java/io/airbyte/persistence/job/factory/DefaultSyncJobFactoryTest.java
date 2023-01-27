/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.DefaultJobCreator;
import io.airbyte.persistence.job.WorkspaceHelper;
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
    final UUID workspaceWebhookConfigId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final String workspaceWebhookName = "test-webhook-name";
    final JsonNode persistedWebhookConfigs = Jsons.deserialize(
        String.format("{\"webhookConfigs\": [{\"id\": \"%s\", \"name\": \"%s\", \"authToken\": {\"_secret\": \"a-secret_v1\"}}]}",
            workspaceWebhookConfigId, workspaceWebhookName));
    final DefaultJobCreator jobCreator = mock(DefaultJobCreator.class);
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final WorkspaceHelper workspaceHelper = mock(WorkspaceHelper.class);
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
    final Version srcProtocolVersion = new Version("0.3.1");

    final String dstDockerRepo = "dstrepo";
    final String dstDockerTag = "tag";
    final String dstDockerImage = DockerUtils.getTaggedImageName(dstDockerRepo, dstDockerTag);
    final Version dstProtocolVersion = new Version("0.3.2");
    final StandardSourceDefinition standardSourceDefinition =
        new StandardSourceDefinition().withSourceDefinitionId(sourceDefinitionId).withDockerRepository(srcDockerRepo)
            .withDockerImageTag(srcDockerTag).withProtocolVersion(srcProtocolVersion.serialize());
    final StandardDestinationDefinition standardDestinationDefinition =
        new StandardDestinationDefinition().withDestinationDefinitionId(destinationDefinitionId).withDockerRepository(dstDockerRepo)
            .withDockerImageTag(dstDockerTag).withProtocolVersion(dstProtocolVersion.serialize());

    when(configRepository.getStandardSync(connectionId)).thenReturn(standardSync);
    when(configRepository.getSourceConnection(sourceId)).thenReturn(sourceConnection);
    when(configRepository.getDestinationConnection(destinationId)).thenReturn(destinationConnection);
    when(configRepository.getStandardSyncOperation(operationId)).thenReturn(operation);
    when(
        jobCreator.createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, srcProtocolVersion, dstDockerImage,
            dstProtocolVersion, operations,
            persistedWebhookConfigs, standardSourceDefinition, standardDestinationDefinition, workspaceId))
                .thenReturn(Optional.of(jobId));
    when(configRepository.getStandardSourceDefinition(sourceDefinitionId))
        .thenReturn(standardSourceDefinition);

    when(configRepository.getStandardDestinationDefinition(destinationDefinitionId))
        .thenReturn(standardDestinationDefinition);

    when(configRepository.getStandardWorkspaceNoSecrets(any(), eq(true))).thenReturn(
        new StandardWorkspace().withWorkspaceId(workspaceId).withWebhookOperationConfigs(persistedWebhookConfigs));

    final SyncJobFactory factory = new DefaultSyncJobFactory(true, jobCreator, configRepository, mock(OAuthConfigSupplier.class), workspaceHelper);
    final long actualJobId = factory.create(connectionId);
    assertEquals(jobId, actualJobId);

    verify(jobCreator)
        .createSyncJob(sourceConnection, destinationConnection, standardSync, srcDockerImage, srcProtocolVersion, dstDockerImage, dstProtocolVersion,
            operations, persistedWebhookConfigs,
            standardSourceDefinition, standardDestinationDefinition, workspaceId);
  }

}
