/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationSearch;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DestinationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationHandler.class);

  private final ConnectionsHandler connectionsHandler;
  private final SpecFetcher specFetcher;
  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSecretsProcessor secretsProcessor;

  @VisibleForTesting
  DestinationHandler(final ConfigRepository configRepository,
      final JsonSchemaValidator integrationSchemaValidation,
      final SpecFetcher specFetcher,
      final ConnectionsHandler connectionsHandler,
      final Supplier<UUID> uuidGenerator,
      final JsonSecretsProcessor secretsProcessor,
      final ConfigurationUpdate configurationUpdate) {
    this.configRepository = configRepository;
    this.validator = integrationSchemaValidation;
    this.specFetcher = specFetcher;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
    this.configurationUpdate = configurationUpdate;
    this.secretsProcessor = secretsProcessor;
  }

  public DestinationHandler(final ConfigRepository configRepository,
      final JsonSchemaValidator integrationSchemaValidation,
      final SpecFetcher specFetcher,
      final ConnectionsHandler connectionsHandler) {
    this(
        configRepository,
        integrationSchemaValidation,
        specFetcher,
        connectionsHandler,
        UUID::randomUUID,
        new JsonSecretsProcessor(),
        new ConfigurationUpdate(configRepository, specFetcher));
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
    // Delete connections first in case it it fails in the middle, destination will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(destination.getWorkspaceId());
    for (final ConnectionRead connectionRead : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getDestinationId().equals(destination.getDestinationId())) {
        continue;
      }

      connectionsHandler.deleteConnection(connectionRead);
    }

    final var fullConfig = configRepository.getDestinationConnectionWithSecrets(destination.getDestinationId()).getConfiguration();

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
    final UUID destinationId = destinationIdRequestBody.getDestinationId();
    final DestinationConnection dci = configRepository.getDestinationConnection(destinationId);

    if (dci.getTombstone()) {
      throw new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString());
    }

    return buildDestinationRead(destinationIdRequestBody.getDestinationId());
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
    return getSpec(specFetcher, configRepository.getStandardDestinationDefinition(destinationDefinitionId));
  }

  public static ConnectorSpecification getSpec(final SpecFetcher specFetcher, final StandardDestinationDefinition destinationDef)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return specFetcher.execute(destinationDef);
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
    configRepository.writeDestinationConnection(destinationConnection, getSpec(destinationDefinitionId));
  }

  private DestinationRead buildDestinationRead(final UUID destinationId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectorSpecification spec = getSpec(configRepository.getDestinationConnection(destinationId).getDestinationDefinitionId());
    return buildDestinationRead(destinationId, spec);
  }

  private DestinationRead buildDestinationRead(final UUID destinationId, final ConnectorSpecification spec)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    // remove secrets from config before returning the read
    final DestinationConnection dci = Jsons.clone(configRepository.getDestinationConnection(destinationId));
    dci.setConfiguration(secretsProcessor.maskSecrets(dci.getConfiguration(), spec.getConnectionSpecification()));

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
