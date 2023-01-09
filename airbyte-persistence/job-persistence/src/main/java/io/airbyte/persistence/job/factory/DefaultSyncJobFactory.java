/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.factory;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.docker.DockerUtils;
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
import java.util.UUID;

public class DefaultSyncJobFactory implements SyncJobFactory {

  private final boolean connectorSpecificResourceDefaultsEnabled;
  private final DefaultJobCreator jobCreator;
  private final ConfigRepository configRepository;
  private final OAuthConfigSupplier oAuthConfigSupplier;
  private final WorkspaceHelper workspaceHelper;

  public DefaultSyncJobFactory(final boolean connectorSpecificResourceDefaultsEnabled,
                               final DefaultJobCreator jobCreator,
                               final ConfigRepository configRepository,
                               final OAuthConfigSupplier oAuthConfigSupplier,
                               final WorkspaceHelper workspaceHelper) {
    this.connectorSpecificResourceDefaultsEnabled = connectorSpecificResourceDefaultsEnabled;
    this.jobCreator = jobCreator;
    this.configRepository = configRepository;
    this.oAuthConfigSupplier = oAuthConfigSupplier;
    this.workspaceHelper = workspaceHelper;
  }

  @Override
  public Long create(final UUID connectionId) {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);
      final UUID workspaceId = workspaceHelper.getWorkspaceForSourceId(standardSync.getSourceId());
      final StandardWorkspace workspace = configRepository.getStandardWorkspaceNoSecrets(workspaceId, true);
      final SourceConnection sourceConnection = configRepository.getSourceConnection(standardSync.getSourceId());
      final DestinationConnection destinationConnection = configRepository.getDestinationConnection(standardSync.getDestinationId());
      final JsonNode sourceConfiguration = oAuthConfigSupplier.injectSourceOAuthParameters(
          sourceConnection.getSourceDefinitionId(),
          sourceConnection.getWorkspaceId(),
          sourceConnection.getConfiguration());
      sourceConnection.withConfiguration(sourceConfiguration);
      final JsonNode destinationConfiguration = oAuthConfigSupplier.injectDestinationOAuthParameters(
          destinationConnection.getDestinationDefinitionId(),
          destinationConnection.getWorkspaceId(),
          destinationConnection.getConfiguration());
      destinationConnection.withConfiguration(destinationConfiguration);
      final StandardSourceDefinition sourceDefinition = configRepository
          .getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
      final StandardDestinationDefinition destinationDefinition = configRepository
          .getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId());

      final String sourceImageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
      final String destinationImageName =
          DockerUtils.getTaggedImageName(destinationDefinition.getDockerRepository(), destinationDefinition.getDockerImageTag());

      final List<StandardSyncOperation> standardSyncOperations = Lists.newArrayList();
      for (final var operationId : standardSync.getOperationIds()) {
        final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
        standardSyncOperations.add(standardSyncOperation);
      }

      // for OSS users, make it possible to ignore default actor-level resource requirements
      if (!connectorSpecificResourceDefaultsEnabled) {
        sourceDefinition.setResourceRequirements(null);
        destinationDefinition.setResourceRequirements(null);
      }

      return jobCreator.createSyncJob(
          sourceConnection,
          destinationConnection,
          standardSync,
          sourceImageName,
          new Version(sourceDefinition.getProtocolVersion()),
          destinationImageName,
          new Version(destinationDefinition.getProtocolVersion()),
          standardSyncOperations,
          workspace.getWebhookOperationConfigs(),
          sourceDefinition,
          destinationDefinition,
          workspace.getWorkspaceId())
          .orElseThrow(() -> new IllegalStateException("We shouldn't be trying to create a new sync job if there is one running already."));

    } catch (final IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

}
