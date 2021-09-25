/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.lang.Exceptions;
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
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpers;
import io.airbyte.config.persistence.split_secrets.SplitSecretConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import org.apache.commons.lang3.NotImplementedException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class ConfigRepository {

  private final ConfigPersistence persistence;
  private final Optional<SecretPersistence> secretPersistence;

  public ConfigRepository(final ConfigPersistence persistence, final Optional<SecretPersistence> secretPersistence) {
    this.persistence = persistence;
    this.secretPersistence = secretPersistence;
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

  public SourceConnection getSourceConnection(final UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
    return persistence.getConfig(ConfigSchema.SOURCE_CONNECTION, sourceId.toString(), SourceConnection.class);
  }

  public SourceConnection getSourceConnectionWithSecrets(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final var source = getSourceConnection(sourceId);

    if (secretPersistence.isPresent()) {
      final var partialConfig = source.getConfiguration();
      final var fullConfig = SecretsHelpers.combineConfig(partialConfig, secretPersistence.get());

      source.setConfiguration(fullConfig);
    }

    return source;
  }

  private Optional<SourceConnection> getOptionalSourceConnection(final UUID sourceId) throws JsonValidationException, IOException {
    try {
      return Optional.of(getSourceConnection(sourceId));
    } catch (ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), source.getConfiguration());

    if (secretPersistence.isPresent()) {
      final var previousSourceConnection = getOptionalSourceConnection(source.getSourceId());
      final var splitConfig = getSplitSourceConfig(previousSourceConnection, source, connectorSpecification);

      splitConfig.getCoordinateToPayload().forEach(secretPersistence.get()::write);

      final var partialSourceConnection = new SourceConnection()
              .withSourceId(source.getSourceId())
              .withName(source.getName())
              .withSourceDefinitionId(source.getSourceDefinitionId())
              .withTombstone(source.getTombstone())
              .withWorkspaceId(source.getWorkspaceId())
              .withConfiguration(splitConfig.getPartialConfig());

      persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), partialSourceConnection);
    } else {
      persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), source);
    }
  }

  private SplitSecretConfig getSplitSourceConfig(final Optional<SourceConnection> previousSource,
                                                 final SourceConnection source,
                                                 final ConnectorSpecification connectorSpecification) {
    Preconditions.checkArgument(secretPersistence.isPresent());

    if (previousSource.isPresent()) {
      return SecretsHelpers.splitAndUpdateConfig(
          source.getWorkspaceId(),
          previousSource.get().getConfiguration(),
          source.getConfiguration(),
          connectorSpecification,
          secretPersistence.get()::read);
    } else {
      return SecretsHelpers.splitConfig(
          source.getWorkspaceId(),
          source.getConfiguration(),
          connectorSpecification);
    }
  }

  public List<SourceConnection> listSourceConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
  }

  public List<SourceConnection> listSourceConnectionWithSecrets() throws JsonValidationException, IOException {
    final var sources = listSourceConnection();

    if(secretPersistence.isPresent()) {
      return sources.stream()
              .map(partialSource -> Exceptions.toRuntime(() -> getSourceConnectionWithSecrets(partialSource.getSourceId())))
              .collect(Collectors.toList());
    } else {
      return sources;
    }
  }

  public DestinationConnection getDestinationConnection(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString(), DestinationConnection.class);
  }

  public DestinationConnection getDestinationConnectionWithSecrets(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final var destination = getDestinationConnection(destinationId);

    if (secretPersistence.isPresent()) {
      final var partialConfig = destination.getConfiguration();
      final var fullConfig = SecretsHelpers.combineConfig(partialConfig, secretPersistence.get());

      destination.setConfiguration(fullConfig);
    }

    return destination;

  }

  private Optional<DestinationConnection> getOptionalDestinationConnection(final UUID destinationId) throws JsonValidationException, IOException {
    try {
      return Optional.of(getDestinationConnection(destinationId));
    } catch (ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeDestinationConnection(final DestinationConnection destination, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), destination.getConfiguration());

    if (secretPersistence.isPresent()) {
      final var previousDestinationConnection = getOptionalSourceConnection(destination.getDestinationId());
      final var splitConfig = getSplitSourceConfig(previousDestinationConnection, destination, connectorSpecification);

      splitConfig.getCoordinateToPayload().forEach(secretPersistence.get()::write);

      final var partialDestinationConnection = new DestinationConnection()
              .withDestinationId(destination.getDestinationId())
              .withName(destination.getName())
              .withDestinationDefinitionId(destination.getDestinationDefinitionId())
              .withTombstone(destination.getTombstone())
              .withWorkspaceId(destination.getWorkspaceId())
              .withConfiguration(splitConfig.getPartialConfig());

      persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, destination.getDestinationId().toString(), partialDestinationConnection);
    } else {
      persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, destination.getDestinationId().toString(), destination);
    }
  }

  private SplitSecretConfig getSplitDestinationConfig(final Optional<DestinationConnection> previousDestination,
                                                      final DestinationConnection destination,
                                                      final ConnectorSpecification connectorSpecification) {
    Preconditions.checkArgument(secretPersistence.isPresent());

    if (previousDestination.isPresent()) {
      return SecretsHelpers.splitAndUpdateConfig(
          destination.getWorkspaceId(),
          previousDestination.get().getConfiguration(),
          destination.getConfiguration(),
          connectorSpecification,
          secretPersistence.get()::read);
    } else {
      return SecretsHelpers.splitConfig(
          destination.getWorkspaceId(),
          destination.getConfiguration(),
          connectorSpecification);
    }
  }

  public List<DestinationConnection> listDestinationConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
  }

  public List<DestinationConnection> listDestinationConnectionWithSecrets() throws JsonValidationException, IOException {
    final var destinations = listDestinationConnection();

    if(secretPersistence.isPresent()) {
      return destinations.stream()
              .map(partialDestination -> Exceptions.toRuntime(() -> getDestinationConnectionWithSecrets(partialDestination.getDestinationId())))
              .collect(Collectors.toList());
    } else {
      return destinations;
    }
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

  // todo: should replaceAllConfigs just write individual configs using their proper call instead of having a
  // replaceAllConfigs at the persistence layer? It'd be slower if there's a batching mechanism, but without it
  // there really isn't a great way of handling secrets injection
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    if(secretPersistence.isPresent()) {
      throw new NotImplementedException();
    } else {
      persistence.replaceAllConfigs(configs, dryRun);
    }
  }

  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final var persistenceMap = persistence.dumpConfigs();
    if(secretPersistence.isPresent()) {
      final var augmentedMap = new HashMap<>(persistenceMap);
      final var sourceKey = ConfigSchema.SOURCE_CONNECTION.name();
      final var destinationKey = ConfigSchema.DESTINATION_CONNECTION.name();

      if(augmentedMap.containsKey(sourceKey)) {
        final Stream<JsonNode> augmentedValue = augmentedMap.get(sourceKey)
                .map(config -> SecretsHelpers.combineConfig(config, secretPersistence.get()));
        augmentedMap.put(sourceKey, augmentedValue);
      }

      if(augmentedMap.containsKey(destinationKey)) {
        final Stream<JsonNode> augmentedValue = augmentedMap.get(destinationKey)
                .map(config -> SecretsHelpers.combineConfig(config, secretPersistence.get()));
        augmentedMap.put(destinationKey, augmentedValue);
      }

      return augmentedMap;
    } else {
      return persistenceMap;
    }
  }

  public void loadData(ConfigPersistence seedPersistence) throws IOException {
    persistence.loadData(seedPersistence);
  }

}
