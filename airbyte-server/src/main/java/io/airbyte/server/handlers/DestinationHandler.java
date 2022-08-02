/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.DestinationCloneConfiguration;
import io.airbyte.api.model.generated.DestinationCloneRequestBody;
import io.airbyte.api.model.generated.DestinationCreate;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.DestinationUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class DestinationHandler {

  private final ConnectionsHandler connectionsHandler;
  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final SecretsRepositoryReader secretsRepositoryReader;
  private final SecretsRepositoryWriter secretsRepositoryWriter;
  private final JsonSchemaValidator validator;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSecretsProcessor secretsProcessor;

  @VisibleForTesting
  DestinationHandler(final ConfigRepository configRepository,
                     final SecretsRepositoryReader secretsRepositoryReader,
                     final SecretsRepositoryWriter secretsRepositoryWriter,
                     final JsonSchemaValidator integrationSchemaValidation,
                     final ConnectionsHandler connectionsHandler,
                     final Supplier<UUID> uuidGenerator,
                     final JsonSecretsProcessor secretsProcessor,
                     final ConfigurationUpdate configurationUpdate) {
    this.configRepository = configRepository;
    this.secretsRepositoryReader = secretsRepositoryReader;
    this.secretsRepositoryWriter = secretsRepositoryWriter;
    this.validator = integrationSchemaValidation;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
    this.configurationUpdate = configurationUpdate;
    this.secretsProcessor = secretsProcessor;
  }

  public DestinationHandler(final ConfigRepository configRepository,
                            final SecretsRepositoryReader secretsRepositoryReader,
                            final SecretsRepositoryWriter secretsRepositoryWriter,
                            final JsonSchemaValidator integrationSchemaValidation,
                            final ConnectionsHandler connectionsHandler) {
    this(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        integrationSchemaValidation,
        connectionsHandler,
        UUID::randomUUID,
        JsonSecretsProcessor.builder()
            .maskSecrets(true)
            .copySecrets(true)
            .build(),
        new ConfigurationUpdate(configRepository, secretsRepositoryReader));
  }

  public DestinationRead createDestination(final DestinationCreate destinationCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    final ConnectorSpecification spec = getSpec(destinationCreate.getDestinationDefinitionId());
    validateDestination(spec, destinationCreate.getConnectionConfiguration());

    // persist
    final UUID destinationId = uuidGenerator.get();
    persistDestinationConnection(
        destinationCreate.getName() != null ? destinationCreate.getName() : "default",
        destinationCreate.getDestinationDefinitionId(),
        destinationCreate.getWorkspaceId(),
        destinationId,
        destinationCreate.getConnectionConfiguration(),
        false);

    // read configuration from db
    return buildDestinationRead(destinationId, spec);
  }

  public void deleteDestination(final DestinationIdRequestBody destinationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing implementation
    final DestinationRead destination = buildDestinationRead(destinationIdRequestBody.getDestinationId());

    deleteDestination(destination);
  }

  public void deleteDestination(final DestinationRead destination)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // disable all connections associated with this destination
    // Delete connections first in case it fails in the middle, destination will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(destination.getWorkspaceId());
    for (final ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getDestinationId().equals(destination.getDestinationId())) {
        continue;
      }

      connectionsHandler.deleteConnection(connectionRead.getConnectionId());
    }

    final var fullConfig = secretsRepositoryReader.getDestinationConnectionWithSecrets(destination.getDestinationId()).getConfiguration();

    // persist
    persistDestinationConnection(
        destination.getName(),
        destination.getDestinationDefinitionId(),
        destination.getWorkspaceId(),
        destination.getDestinationId(),
        fullConfig,
        true);
  }

  public DestinationRead updateDestination(final DestinationUpdate destinationUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // get existing implementation
    final DestinationConnection updatedDestination = configurationUpdate
        .destination(destinationUpdate.getDestinationId(), destinationUpdate.getName(), destinationUpdate.getConnectionConfiguration());

    final ConnectorSpecification spec = getSpec(updatedDestination.getDestinationDefinitionId());

    // validate configuration
    validateDestination(spec, updatedDestination.getConfiguration());

    // persist
    persistDestinationConnection(
        updatedDestination.getName(),
        updatedDestination.getDestinationDefinitionId(),
        updatedDestination.getWorkspaceId(),
        updatedDestination.getDestinationId(),
        updatedDestination.getConfiguration(),
        updatedDestination.getTombstone());

    // read configuration from db
    return buildDestinationRead(destinationUpdate.getDestinationId(), spec);
  }

  public DestinationRead getDestination(final DestinationIdRequestBody destinationIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildDestinationRead(destinationIdRequestBody.getDestinationId());
  }

  public DestinationRead cloneDestination(final DestinationCloneRequestBody destinationCloneRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // read destination configuration from db
    final DestinationRead destinationToClone = buildDestinationReadWithSecrets(destinationCloneRequestBody.getDestinationCloneId());
    final DestinationCloneConfiguration destinationCloneConfiguration = destinationCloneRequestBody.getDestinationConfiguration();

    final String copyText = " (Copy)";
    final String destinationName = destinationToClone.getName() + copyText;

    final DestinationCreate destinationCreate = new DestinationCreate()
        .name(destinationName)
        .destinationDefinitionId(destinationToClone.getDestinationDefinitionId())
        .connectionConfiguration(destinationToClone.getConnectionConfiguration())
        .workspaceId(destinationToClone.getWorkspaceId());

    if (destinationCloneConfiguration != null) {
      if (destinationCloneConfiguration.getName() != null) {
        destinationCreate.name(destinationCloneConfiguration.getName());
      }

      if (destinationCloneConfiguration.getConnectionConfiguration() != null) {
        destinationCreate.connectionConfiguration(destinationCloneConfiguration.getConnectionConfiguration());
      }
    }

    return createDestination(destinationCreate);
  }

  public DestinationReadList listDestinationsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationRead> reads = Lists.newArrayList();

    for (final DestinationConnection dci : configRepository.listDestinationConnection()) {
      if (!dci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }

      if (dci.getTombstone()) {
        continue;
      }

      reads.add(buildDestinationRead(dci.getDestinationId()));
    }

    return new DestinationReadList().destinations(reads);
  }

  public DestinationReadList listDestinationsForDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final List<DestinationRead> reads = Lists.newArrayList();

    for (final DestinationConnection destinationConnection : configRepository.listDestinationConnection()) {
      if (!destinationConnection.getDestinationDefinitionId().equals(destinationDefinitionIdRequestBody.getDestinationDefinitionId())) {
        continue;
      }
      if (destinationConnection.getTombstone() != null && destinationConnection.getTombstone()) {
        continue;
      }

      reads.add(buildDestinationRead(destinationConnection.getDestinationId()));
    }

    return new DestinationReadList().destinations(reads);
  }

  public DestinationReadList searchDestinations(final DestinationSearch destinationSearch)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationRead> reads = Lists.newArrayList();

    for (final DestinationConnection dci : configRepository.listDestinationConnection()) {
      if (!dci.getTombstone()) {
        final DestinationRead destinationRead = buildDestinationRead(dci.getDestinationId());
        if (connectionsHandler.matchSearch(destinationSearch, destinationRead)) {
          reads.add(destinationRead);
        }
      }
    }

    return new DestinationReadList().destinations(reads);
  }

  private void validateDestination(final ConnectorSpecification spec, final JsonNode configuration) throws JsonValidationException {
    validator.ensure(spec.getConnectionSpecification(), configuration);
  }

  public ConnectorSpecification getSpec(final UUID destinationDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return configRepository.getStandardDestinationDefinition(destinationDefinitionId).getSpec();
  }

  private void persistDestinationConnection(final String name,
                                            final UUID destinationDefinitionId,
                                            final UUID workspaceId,
                                            final UUID destinationId,
                                            final JsonNode configurationJson,
                                            final boolean tombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationConnection destinationConnection = new DestinationConnection()
        .withName(name)
        .withDestinationDefinitionId(destinationDefinitionId)
        .withWorkspaceId(workspaceId)
        .withDestinationId(destinationId)
        .withConfiguration(configurationJson)
        .withTombstone(tombstone);
    secretsRepositoryWriter.writeDestinationConnection(destinationConnection, getSpec(destinationDefinitionId));
  }

  private DestinationRead buildDestinationRead(final UUID destinationId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectorSpecification spec = getSpec(configRepository.getDestinationConnection(destinationId).getDestinationDefinitionId());
    return buildDestinationRead(destinationId, spec);
  }

  private DestinationRead buildDestinationRead(final UUID destinationId, final ConnectorSpecification spec)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    // remove secrets from config before returning the read
    final DestinationConnection dci = Jsons.clone(configRepository.getDestinationConnection(destinationId));
    dci.setConfiguration(secretsProcessor.prepareSecretsForOutput(dci.getConfiguration(), spec.getConnectionSpecification()));

    final StandardDestinationDefinition standardDestinationDefinition =
        configRepository.getStandardDestinationDefinition(dci.getDestinationDefinitionId());
    return toDestinationRead(dci, standardDestinationDefinition);
  }

  private DestinationRead buildDestinationReadWithSecrets(final UUID destinationId)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    // remove secrets from config before returning the read
    final DestinationConnection dci = Jsons.clone(secretsRepositoryReader.getDestinationConnectionWithSecrets(destinationId));
    final StandardDestinationDefinition standardDestinationDefinition =
        configRepository.getStandardDestinationDefinition(dci.getDestinationDefinitionId());
    return toDestinationRead(dci, standardDestinationDefinition);
  }

  protected static DestinationRead toDestinationRead(final DestinationConnection destinationConnection,
                                                     final StandardDestinationDefinition standardDestinationDefinition) {
    return new DestinationRead()
        .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .destinationId(destinationConnection.getDestinationId())
        .workspaceId(destinationConnection.getWorkspaceId())
        .destinationDefinitionId(destinationConnection.getDestinationDefinitionId())
        .connectionConfiguration(destinationConnection.getConfiguration())
        .name(destinationConnection.getName())
        .destinationName(standardDestinationDefinition.getName());
  }

}
