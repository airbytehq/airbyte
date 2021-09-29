/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;

public class ConfigRepository {

  private final ConfigPersistence persistence;

  public ConfigRepository(final ConfigPersistence persistence) {
    this.persistence = persistence;
  }

  public StandardWorkspace getStandardWorkspace(final UUID workspaceId, final boolean includeTombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = persistence.getConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), StandardWorkspace.class);

    if (!MoreBooleans.isTruthy(workspace.getTombstone()) || includeTombstone) {
      return workspace;
    }

    throw new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString());
  }

  public Optional<StandardWorkspace> getWorkspaceBySlugOptional(final String slug, final boolean includeTombstone)
      throws JsonValidationException, IOException {
    for (final StandardWorkspace workspace : listStandardWorkspaces(includeTombstone)) {
      if (workspace.getSlug().equals(slug)) {
        return Optional.of(workspace);
      }
    }
    return Optional.empty();
  }

  public StandardWorkspace getWorkspaceBySlug(final String slug, final boolean includeTombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return getWorkspaceBySlugOptional(slug, includeTombstone).orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, slug));
  }

  public List<StandardWorkspace> listStandardWorkspaces(final boolean includeTombstone) throws JsonValidationException, IOException {

    final List<StandardWorkspace> workspaces = new ArrayList<>();

    for (final StandardWorkspace workspace : persistence.listConfigs(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class)) {
      if (!MoreBooleans.isTruthy(workspace.getTombstone()) || includeTombstone) {
        workspaces.add(workspace);
      }
    }

    return workspaces;
  }

  public void writeStandardWorkspace(final StandardWorkspace workspace) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), workspace);
  }

  public StandardSourceDefinition getStandardSourceDefinition(final UUID sourceDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinitionId.toString(), StandardSourceDefinition.class);
  }

  public StandardSourceDefinition getSourceDefinitionFromSource(final UUID sourceId) {
    try {
      final SourceConnection source = getSourceConnection(sourceId);
      return getStandardSourceDefinition(source.getSourceDefinitionId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public StandardSourceDefinition getSourceDefinitionFromConnection(final UUID connectionId) {
    try {
      final StandardSync sync = getStandardSync(connectionId);
      return getSourceDefinitionFromSource(sync.getSourceId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public List<StandardSourceDefinition> listStandardSources() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
  }

  public void writeStandardSource(final StandardSourceDefinition source) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
  }

  public StandardDestinationDefinition getStandardDestinationDefinition(final UUID destinationDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationDefinitionId.toString(),
        StandardDestinationDefinition.class);
  }

  public StandardDestinationDefinition getDestinationDefinitionFromDestination(final UUID destinationId) {
    try {
      final DestinationConnection destination = getDestinationConnection(destinationId);
      return getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public StandardDestinationDefinition getDestinationDefinitionFromConnection(final UUID connectionId) {
    try {
      final StandardSync sync = getStandardSync(connectionId);
      return getDestinationDefinitionFromDestination(sync.getDestinationId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public List<StandardDestinationDefinition> listStandardDestinationDefinitions() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
  }

  public void writeStandardDestinationDefinition(final StandardDestinationDefinition destinationDefinition)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        destinationDefinition.getDestinationDefinitionId().toString(),
        destinationDefinition);
  }

  public SourceConnection getSourceConnection(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.SOURCE_CONNECTION, sourceId.toString(), SourceConnection.class);
  }

  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), source.getConfiguration());

    persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), source);
  }

  public List<SourceConnection> listSourceConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
  }

  public DestinationConnection getDestinationConnection(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString(), DestinationConnection.class);
  }

  public void writeDestinationConnection(final DestinationConnection destinationConnection, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), destinationConnection.getConfiguration());

    persistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, destinationConnection.getDestinationId().toString(), destinationConnection);
  }

  public List<DestinationConnection> listDestinationConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
  }

  public StandardSync getStandardSync(final UUID connectionId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
  }

  public void writeStandardSync(final StandardSync standardSync) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SYNC, standardSync.getConnectionId().toString(), standardSync);
  }

  public List<StandardSync> listStandardSyncs() throws ConfigNotFoundException, IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
  }

  public StandardSyncOperation getStandardSyncOperation(final UUID operationId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString(), StandardSyncOperation.class);
  }

  public void writeStandardSyncOperation(final StandardSyncOperation standardSyncOperation) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SYNC_OPERATION, standardSyncOperation.getOperationId().toString(), standardSyncOperation);
  }

  public List<StandardSyncOperation> listStandardSyncOperations() throws IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC_OPERATION, StandardSyncOperation.class);
  }

  public SourceOAuthParameter getSourceOAuthParams(final UUID SourceOAuthParameterId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameterId.toString(), SourceOAuthParameter.class);
  }

  public Optional<SourceOAuthParameter> getSourceOAuthParamByDefinitionIdOptional(final UUID workspaceId, final UUID sourceDefinitionId)
      throws JsonValidationException, IOException {
    for (final SourceOAuthParameter oAuthParameter : listSourceOAuthParam()) {
      if (sourceDefinitionId.equals(oAuthParameter.getSourceDefinitionId()) &&
          Objects.equals(workspaceId, oAuthParameter.getWorkspaceId())) {
        return Optional.of(oAuthParameter);
      }
    }
    return Optional.empty();
  }

  public void writeSourceOAuthParam(final SourceOAuthParameter SourceOAuthParameter) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.getOauthParameterId().toString(), SourceOAuthParameter);
  }

  public List<SourceOAuthParameter> listSourceOAuthParam() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.class);
  }

  public DestinationOAuthParameter getDestinationOAuthParams(final UUID destinationOAuthParameterId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.DESTINATION_OAUTH_PARAM, destinationOAuthParameterId.toString(), DestinationOAuthParameter.class);
  }

  public Optional<DestinationOAuthParameter> getDestinationOAuthParamByDefinitionIdOptional(final UUID workspaceId,
                                                                                            final UUID destinationDefinitionId)
      throws JsonValidationException, IOException {
    for (final DestinationOAuthParameter oAuthParameter : listDestinationOAuthParam()) {
      if (destinationDefinitionId.equals(oAuthParameter.getDestinationDefinitionId()) &&
          Objects.equals(workspaceId, oAuthParameter.getWorkspaceId())) {
        return Optional.of(oAuthParameter);
      }
    }
    return Optional.empty();
  }

  public void writeDestinationOAuthParam(final DestinationOAuthParameter destinationOAuthParameter) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.DESTINATION_OAUTH_PARAM, destinationOAuthParameter.getOauthParameterId().toString(),
        destinationOAuthParameter);
  }

  public List<DestinationOAuthParameter> listDestinationOAuthParam() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_OAUTH_PARAM, DestinationOAuthParameter.class);
  }

  /**
   * Converts between a dumpConfig() output and a replaceAllConfigs() input, by deserializing the
   * string/jsonnode into the AirbyteConfig, Stream<Object<AirbyteConfig.getClassName()>
   *
   * @param configurations from dumpConfig()
   * @return input suitable for replaceAllConfigs()
   */
  public static Map<AirbyteConfig, Stream<?>> deserialize(Map<String, Stream<JsonNode>> configurations) {
    Map<AirbyteConfig, Stream<?>> deserialized = new LinkedHashMap<AirbyteConfig, Stream<?>>();
    for (String configSchemaName : configurations.keySet()) {
      deserialized.put(ConfigSchema.valueOf(configSchemaName),
          configurations.get(configSchemaName).map(jsonNode -> Jsons.object(jsonNode, ConfigSchema.valueOf(configSchemaName).getClassName())));
    }
    return deserialized;
  }

  public void replaceAllConfigsDeserializing(final Map<String, Stream<JsonNode>> configs, final boolean dryRun) throws IOException {
    replaceAllConfigs(deserialize(configs), dryRun);
  }

  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    persistence.replaceAllConfigs(configs, dryRun);
  }

  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    return persistence.dumpConfigs();
  }

  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    persistence.loadData(seedPersistence);
  }

}
