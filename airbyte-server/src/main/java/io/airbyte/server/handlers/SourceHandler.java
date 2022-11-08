/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.SourceCloneConfiguration;
import io.airbyte.api.model.generated.SourceCloneRequestBody;
import io.airbyte.api.model.generated.SourceCreate;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
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

public class SourceHandler {

  private final Supplier<UUID> uuidGenerator;
  private final ConfigRepository configRepository;
  private final SecretsRepositoryReader secretsRepositoryReader;
  private final SecretsRepositoryWriter secretsRepositoryWriter;
  private final JsonSchemaValidator validator;
  private final ConnectionsHandler connectionsHandler;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSecretsProcessor secretsProcessor;

  SourceHandler(final ConfigRepository configRepository,
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
    validator = integrationSchemaValidation;
    this.connectionsHandler = connectionsHandler;
    this.uuidGenerator = uuidGenerator;
    this.configurationUpdate = configurationUpdate;
    this.secretsProcessor = secretsProcessor;
  }

  public SourceHandler(final ConfigRepository configRepository,
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
            .copySecrets(true)
            .build(),
        new ConfigurationUpdate(configRepository, secretsRepositoryReader));
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
    return buildSourceRead(configRepository.getSourceConnection(sourceId), spec);
  }

  public SourceRead updateSource(final SourceUpdate sourceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final UUID sourceId = sourceUpdate.getSourceId();
    final SourceConnection updatedSource = configurationUpdate
        .source(sourceId, sourceUpdate.getName(),
            sourceUpdate.getConnectionConfiguration());
    final ConnectorSpecification spec = getSpecFromSourceId(sourceId);
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
    return buildSourceRead(configRepository.getSourceConnection(sourceId), spec);
  }

  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildSourceRead(sourceIdRequestBody.getSourceId());
  }

  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // read source configuration from db
    final SourceRead sourceToClone = buildSourceReadWithSecrets(sourceCloneRequestBody.getSourceCloneId());
    final SourceCloneConfiguration sourceCloneConfiguration = sourceCloneRequestBody.getSourceConfiguration();

    final String copyText = " (Copy)";
    final String sourceName = sourceToClone.getName() + copyText;

    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceName)
        .sourceDefinitionId(sourceToClone.getSourceDefinitionId())
        .connectionConfiguration(sourceToClone.getConnectionConfiguration())
        .workspaceId(sourceToClone.getWorkspaceId());

    if (sourceCloneConfiguration != null) {
      if (sourceCloneConfiguration.getName() != null) {
        sourceCreate.name(sourceCloneConfiguration.getName());
      }

      if (sourceCloneConfiguration.getConnectionConfiguration() != null) {
        sourceCreate.connectionConfiguration(sourceCloneConfiguration.getConnectionConfiguration());
      }
    }

    return createSource(sourceCreate);
  }

  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<SourceConnection> sourceConnections = configRepository.listWorkspaceSourceConnection(workspaceIdRequestBody.getWorkspaceId());

    final List<SourceRead> reads = Lists.newArrayList();
    for (final SourceConnection sc : sourceConnections) {
      reads.add(buildSourceRead(sc));
    }

    return new SourceReadList().sources(reads);
  }

  public SourceReadList listSourcesForSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {

    final List<SourceRead> reads = Lists.newArrayList();
    for (final SourceConnection sourceConnection : configRepository.listSourcesForDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId())) {
      reads.add(buildSourceRead(sourceConnection));
    }

    return new SourceReadList().sources(reads);
  }

  public SourceReadList searchSources(final SourceSearch sourceSearch)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = Lists.newArrayList();

    for (final SourceConnection sci : configRepository.listSourceConnection()) {
      if (!sci.getTombstone()) {
        final SourceRead sourceRead = buildSourceRead(sci);
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
    // Delete connections first in case it fails in the middle, source will still be visible
    final var workspaceIdRequestBody = new WorkspaceIdRequestBody()
        .workspaceId(source.getWorkspaceId());

    connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)
        .getConnections().stream()
        .filter(con -> con.getSourceId().equals(source.getSourceId()))
        .map(ConnectionRead::getConnectionId)
        .forEach(connectionsHandler::deleteConnection);

    final var spec = getSpecFromSourceId(source.getSourceId());
    final var fullConfig = secretsRepositoryReader.getSourceConnectionWithSecrets(source.getSourceId()).getConfiguration();

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
    final SourceConnection sourceConnection = configRepository.getSourceConnection(sourceId);
    return buildSourceRead(sourceConnection);
  }

  private SourceRead buildSourceRead(final SourceConnection sourceConnection)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId());
    final ConnectorSpecification spec = sourceDef.getSpec();
    return buildSourceRead(sourceConnection, spec);
  }

  private SourceRead buildSourceRead(final SourceConnection sourceConnection, final ConnectorSpecification spec)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final StandardSourceDefinition standardSourceDefinition = configRepository
        .getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
    final JsonNode sanitizedConfig = secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), spec.getConnectionSpecification());
    sourceConnection.setConfiguration(sanitizedConfig);
    return toSourceRead(sourceConnection, standardSourceDefinition);
  }

  private SourceRead buildSourceReadWithSecrets(final UUID sourceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read configuration from db
    final SourceConnection sourceConnection = secretsRepositoryReader.getSourceConnectionWithSecrets(sourceId);
    final StandardSourceDefinition standardSourceDefinition = configRepository
        .getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
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
    return sourceDef.getSpec();
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

    secretsRepositoryWriter.writeSourceConnection(sourceConnection, spec);
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
        .name(sourceConnection.getName())
        .icon(SourceDefinitionsHandler.loadIcon(standardSourceDefinition.getIcon()));
  }

}
