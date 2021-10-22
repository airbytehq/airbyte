/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceSearch;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
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

public class SourceHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;
  private final SpecFetcher specFetcher;
  private final ConnectionsHandler connectionsHandler;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSecretsProcessor secretsProcessor;

  SourceHandler(final ConfigRepository configRepository,
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

  public SourceHandler(final ConfigRepository configRepository,
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

  public SourceRead createSource(final SourceCreate sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // validate configuration
    final ConnectorSpecification spec = getSpecFromSourceDefinitionId(
        sourceCreate.getSourceDefinitionId());
    validateSource(spec, sourceCreate.getConnectionConfiguration());

    // persist
    final UUID sourceId = uuidGenerator.get();
    persistSourceConnection(
        sourceCreate.getName() != null ? sourceCreate.getName() : "default",
        sourceCreate.getSourceDefinitionId(),
        sourceCreate.getWorkspaceId(),
        sourceId,
        false,
        sourceCreate.getConnectionConfiguration(),
        spec);

    // read configuration from db
    return buildSourceRead(sourceId, spec);
  }

  public SourceRead updateSource(final SourceUpdate sourceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final SourceConnection updatedSource = configurationUpdate
        .source(sourceUpdate.getSourceId(), sourceUpdate.getName(),
            sourceUpdate.getConnectionConfiguration());
    final ConnectorSpecification spec = getSpecFromSourceId(updatedSource.getSourceId());
    validateSource(spec, sourceUpdate.getConnectionConfiguration());

    // persist
    persistSourceConnection(
        updatedSource.getName(),
        updatedSource.getSourceDefinitionId(),
        updatedSource.getWorkspaceId(),
        updatedSource.getSourceId(),
        updatedSource.getTombstone(),
        updatedSource.getConfiguration(),
        spec);

    // read configuration from db
    return buildSourceRead(sourceUpdate.getSourceId(), spec);
  }

  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID sourceId = sourceIdRequestBody.getSourceId();
    final SourceConnection sourceConnection = configRepository.getSourceConnection(sourceId);

    if (sourceConnection.getTombstone()) {
      throw new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION, sourceId.toString());
    }

    return buildSourceRead(sourceId);
  }

  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = Lists.newArrayList();

    for (final SourceConnection sci : configRepository.listSourceConnection()) {
      if (!sci.getWorkspaceId().equals(workspaceIdRequestBody.getWorkspaceId())) {
        continue;
      }
      if (sci.getTombstone()) {
        continue;
      }

      reads.add(buildSourceRead(sci.getSourceId()));
    }

    return new SourceReadList().sources(reads);
  }

  public SourceReadList searchSources(final SourceSearch sourceSearch)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = Lists.newArrayList();

    for (final SourceConnection sci : configRepository.listSourceConnection()) {
      if (!sci.getTombstone()) {
        final SourceRead sourceRead = buildSourceRead(sci.getSourceId());
        if (connectionsHandler.matchSearch(sourceSearch, sourceRead)) {
          reads.add(sourceRead);
        }
      }
    }

    return new SourceReadList().sources(reads);
  }

  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // get existing source
    final SourceRead source = buildSourceRead(sourceIdRequestBody.getSourceId());
    deleteSource(source);
  }

  public void deleteSource(final SourceRead source)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // "delete" all connections associated with source as well.
    // Delete connections first in case it it fails in the middle, source will still be visible
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(source.getWorkspaceId());
    for (final ConnectionRead connectionRead : connectionsHandler
        .listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      if (!connectionRead.getSourceId().equals(source.getSourceId())) {
        continue;
      }

      connectionsHandler.deleteConnection(connectionRead);
    }

    final ConnectorSpecification spec = getSpecFromSourceId(source.getSourceId());
    validateSource(spec, source.getConnectionConfiguration());

    final var fullConfig = configRepository.getSourceConnectionWithSecrets(source.getSourceId()).getConfiguration();
    validateSource(spec, fullConfig);

    // persist
    persistSourceConnection(
        source.getName(),
        source.getSourceDefinitionId(),
        source.getWorkspaceId(),
        source.getSourceId(),
        true,
        fullConfig,
        spec);
  }

  private SourceRead buildSourceRead(final UUID sourceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final StandardSourceDefinition sourceDef = configRepository
        .getSourceDefinitionFromSource(sourceId);
    final ConnectorSpecification spec = specFetcher.execute(sourceDef);
    return buildSourceRead(sourceId, spec);
  }

  private SourceRead buildSourceRead(final UUID sourceId, final ConnectorSpecification spec)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final SourceConnection sourceConnection = configRepository.getSourceConnection(sourceId);
    final StandardSourceDefinition standardSourceDefinition = configRepository
        .getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
    final JsonNode sanitizedConfig = secretsProcessor.maskSecrets(
        sourceConnection.getConfiguration(), spec.getConnectionSpecification());
    sourceConnection.setConfiguration(sanitizedConfig);
    return toSourceRead(sourceConnection, standardSourceDefinition);
  }

  private void validateSource(final ConnectorSpecification spec, final JsonNode implementationJson)
      throws JsonValidationException {
    validator.ensure(spec.getConnectionSpecification(), implementationJson);
  }

  private ConnectorSpecification getSpecFromSourceId(final UUID sourceId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = configRepository.getSourceConnection(sourceId);
    return getSpecFromSourceDefinitionId(source.getSourceDefinitionId());
  }

  private ConnectorSpecification getSpecFromSourceDefinitionId(final UUID sourceDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceDefId);
    return getSpecFromSourceDefinitionId(specFetcher, sourceDef);
  }

  public static ConnectorSpecification getSpecFromSourceDefinitionId(final SpecFetcher specFetcher, final StandardSourceDefinition sourceDefinition)
      throws IOException, ConfigNotFoundException {
    return specFetcher.execute(sourceDefinition);
  }

  private void persistSourceConnection(final String name,
      final UUID sourceDefinitionId,
      final UUID workspaceId,
      final UUID sourceId,
      final boolean tombstone,
      final JsonNode configurationJson,
      final ConnectorSpecification spec)
      throws JsonValidationException, IOException {
    final SourceConnection sourceConnection = new SourceConnection()
        .withName(name)
        .withSourceDefinitionId(sourceDefinitionId)
        .withWorkspaceId(workspaceId)
        .withSourceId(sourceId)
        .withTombstone(tombstone)
        .withConfiguration(configurationJson);

    configRepository.writeSourceConnection(sourceConnection, spec);
  }

  protected static SourceRead toSourceRead(final SourceConnection sourceConnection,
      final StandardSourceDefinition standardSourceDefinition) {
    return new SourceRead()
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .sourceName(standardSourceDefinition.getName())
        .sourceId(sourceConnection.getSourceId())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(sourceConnection.getSourceDefinitionId())
        .connectionConfiguration(sourceConnection.getConfiguration())
        .name(sourceConnection.getName());
  }

}
