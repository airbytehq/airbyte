/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
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
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.config.persistence.split_secrets.SplitSecretConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigRepository {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigRepository.class);

  private static final UUID NO_WORKSPACE = UUID.fromString("00000000-0000-0000-0000-000000000000");

  private final ConfigPersistence persistence;
  private final SecretsHydrator secretsHydrator;
  private final Optional<SecretPersistence> longLivedSecretPersistence;
  private final Optional<SecretPersistence> ephemeralSecretPersistence;
  private Function<String, ConnectorSpecification> specFetcherFn;

  public ConfigRepository(final ConfigPersistence persistence,
                          final SecretsHydrator secretsHydrator,
                          final Optional<SecretPersistence> longLivedSecretPersistence,
                          final Optional<SecretPersistence> ephemeralSecretPersistence) {
    this.persistence = persistence;
    this.secretsHydrator = secretsHydrator;
    this.longLivedSecretPersistence = longLivedSecretPersistence;
    this.ephemeralSecretPersistence = ephemeralSecretPersistence;
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

  public List<StandardSourceDefinition> listStandardSourceDefinitions() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
  }

  public void writeStandardSourceDefinition(final StandardSourceDefinition sourceDefinition) throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceDefinition.getSourceDefinitionId().toString(),
        sourceDefinition);
  }

  public void deleteStandardSourceDefinition(final UUID sourceDefId) throws IOException {
    try {
      persistence.deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefId.toString());
    } catch (final ConfigNotFoundException e) {
      LOGGER.info("Attempted to delete source definition with id: {}, but it does not exist", sourceDefId);
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

  public void deleteStandardDestinationDefinition(final UUID destDefId) throws IOException {
    try {
      persistence.deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destDefId.toString());
    } catch (final ConfigNotFoundException e) {
      LOGGER.info("Attempted to delete destination definition with id: {}, but it does not exist", destDefId);
    }
  }

  public SourceConnection getSourceConnection(final UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
    return persistence.getConfig(ConfigSchema.SOURCE_CONNECTION, sourceId.toString(), SourceConnection.class);
  }

  public SourceConnection getSourceConnectionWithSecrets(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final var source = getSourceConnection(sourceId);
    final var fullConfig = secretsHydrator.hydrate(source.getConfiguration());
    return Jsons.clone(source).withConfiguration(fullConfig);
  }

  private Optional<SourceConnection> getOptionalSourceConnection(final UUID sourceId) throws JsonValidationException, IOException {
    try {
      return Optional.of(getSourceConnection(sourceId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), source.getConfiguration());

    final var previousSourceConnection = getOptionalSourceConnection(source.getSourceId())
        .map(SourceConnection::getConfiguration);

    final var partialConfig =
        statefulUpdateSecrets(source.getWorkspaceId(), previousSourceConnection, source.getConfiguration(), connectorSpecification);
    final var partialSource = Jsons.clone(source).withConfiguration(partialConfig);

    persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), partialSource);
  }

  /**
   *
   * @param workspaceId workspace id for the config
   * @param fullConfig full config
   * @param spec connector specification
   * @return partial config
   */
  public JsonNode statefulSplitSecrets(final UUID workspaceId, final JsonNode fullConfig, final ConnectorSpecification spec) {
    return splitSecretConfig(workspaceId, fullConfig, spec, longLivedSecretPersistence);
  }

  /**
   *
   * @param workspaceId workspace id for the config
   * @param oldConfig old full config
   * @param fullConfig new full config
   * @param spec connector specification
   * @return partial config
   */
  public JsonNode statefulUpdateSecrets(final UUID workspaceId,
                                        final Optional<JsonNode> oldConfig,
                                        final JsonNode fullConfig,
                                        final ConnectorSpecification spec) {
    if (longLivedSecretPersistence.isPresent()) {
      if (oldConfig.isPresent()) {
        final var splitSecretConfig = SecretsHelpers.splitAndUpdateConfig(
            workspaceId,
            oldConfig.get(),
            fullConfig,
            spec,
            longLivedSecretPersistence.get());

        splitSecretConfig.getCoordinateToPayload().forEach(longLivedSecretPersistence.get()::write);

        return splitSecretConfig.getPartialConfig();
      } else {
        final var splitSecretConfig = SecretsHelpers.splitConfig(
            workspaceId,
            fullConfig,
            spec);

        splitSecretConfig.getCoordinateToPayload().forEach(longLivedSecretPersistence.get()::write);

        return splitSecretConfig.getPartialConfig();
      }
    } else {
      return fullConfig;
    }
  }

  /**
   *
   * @param fullConfig full config
   * @param spec connector specification
   * @return partial config
   */
  public JsonNode statefulSplitEphemeralSecrets(final JsonNode fullConfig, final ConnectorSpecification spec) {
    return splitSecretConfig(NO_WORKSPACE, fullConfig, spec, ephemeralSecretPersistence);
  }

  private JsonNode splitSecretConfig(final UUID workspaceId,
                                     final JsonNode fullConfig,
                                     final ConnectorSpecification spec,
                                     final Optional<SecretPersistence> secretPersistence) {
    if (secretPersistence.isPresent()) {
      final SplitSecretConfig splitSecretConfig = SecretsHelpers.splitConfig(workspaceId, fullConfig, spec);
      splitSecretConfig.getCoordinateToPayload().forEach(secretPersistence.get()::write);
      return splitSecretConfig.getPartialConfig();
    } else {
      return fullConfig;
    }
  }

  public List<SourceConnection> listSourceConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
  }

  public List<SourceConnection> listSourceConnectionWithSecrets() throws JsonValidationException, IOException {
    final var sources = listSourceConnection();

    return sources.stream()
        .map(partialSource -> Exceptions.toRuntime(() -> getSourceConnectionWithSecrets(partialSource.getSourceId())))
        .collect(Collectors.toList());
  }

  public DestinationConnection getDestinationConnection(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString(), DestinationConnection.class);
  }

  public DestinationConnection getDestinationConnectionWithSecrets(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final var destination = getDestinationConnection(destinationId);
    final var fullConfig = secretsHydrator.hydrate(destination.getConfiguration());
    return Jsons.clone(destination).withConfiguration(fullConfig);
  }

  private Optional<DestinationConnection> getOptionalDestinationConnection(final UUID destinationId) throws JsonValidationException, IOException {
    try {
      return Optional.of(getDestinationConnection(destinationId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeDestinationConnection(final DestinationConnection destination, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    // actual validation is only for sanity checking
    final JsonSchemaValidator validator = new JsonSchemaValidator();
    validator.ensure(connectorSpecification.getConnectionSpecification(), destination.getConfiguration());

    final var previousDestinationConnection = getOptionalDestinationConnection(destination.getDestinationId())
        .map(DestinationConnection::getConfiguration);

    final var partialConfig =
        statefulUpdateSecrets(destination.getWorkspaceId(), previousDestinationConnection, destination.getConfiguration(), connectorSpecification);
    final var partialDestination = Jsons.clone(destination).withConfiguration(partialConfig);

    persistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, destination.getDestinationId().toString(), partialDestination);
  }

  public List<DestinationConnection> listDestinationConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
  }

  public List<DestinationConnection> listDestinationConnectionWithSecrets() throws JsonValidationException, IOException {
    final var destinations = listDestinationConnection();

    return destinations.stream()
        .map(partialDestination -> Exceptions.toRuntime(() -> getDestinationConnectionWithSecrets(partialDestination.getDestinationId())))
        .collect(Collectors.toList());
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
  public static Map<AirbyteConfig, Stream<?>> deserialize(final Map<String, Stream<JsonNode>> configurations) {
    final Map<AirbyteConfig, Stream<?>> deserialized = new LinkedHashMap<AirbyteConfig, Stream<?>>();
    for (final String configSchemaName : configurations.keySet()) {
      deserialized.put(ConfigSchema.valueOf(configSchemaName),
          configurations.get(configSchemaName).map(jsonNode -> Jsons.object(jsonNode, ConfigSchema.valueOf(configSchemaName).getClassName())));
    }
    return deserialized;
  }

  public void replaceAllConfigsDeserializing(final Map<String, Stream<JsonNode>> configs, final boolean dryRun) throws IOException {
    replaceAllConfigs(deserialize(configs), dryRun);
  }

  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    if (longLivedSecretPersistence.isPresent()) {
      final var augmentedMap = new HashMap<>(configs);

      // get all source defs so that we can use their specs when storing secrets.
      @SuppressWarnings("unchecked")
      final List<StandardSourceDefinition> sourceDefs =
          (List<StandardSourceDefinition>) augmentedMap.get(ConfigSchema.STANDARD_SOURCE_DEFINITION).collect(Collectors.toList());
      // restore data in the map that gets consumed downstream.
      augmentedMap.put(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefs.stream());
      final Map<UUID, ConnectorSpecification> sourceDefIdToSpec = sourceDefs
          .stream()
          .collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId, sourceDefinition -> {
            final String imageName = DockerUtils
                .getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
            return specFetcherFn.apply(imageName);
          }));

      // get all destination defs so that we can use their specs when storing secrets.
      @SuppressWarnings("unchecked")
      final List<StandardDestinationDefinition> destinationDefs =
          (List<StandardDestinationDefinition>) augmentedMap.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION).collect(Collectors.toList());
      augmentedMap.put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationDefs.stream());
      final Map<UUID, ConnectorSpecification> destinationDefIdToSpec = destinationDefs
          .stream()
          .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId, destinationDefinition -> {
            final String imageName = DockerUtils
                .getTaggedImageName(destinationDefinition.getDockerRepository(), destinationDefinition.getDockerImageTag());
            return specFetcherFn.apply(imageName);
          }));

      if (augmentedMap.containsKey(ConfigSchema.SOURCE_CONNECTION)) {
        final Stream<?> augmentedValue = augmentedMap.get(ConfigSchema.SOURCE_CONNECTION)
            .map(config -> {
              final SourceConnection source = (SourceConnection) config;

              if (!sourceDefIdToSpec.containsKey(source.getSourceDefinitionId())) {
                throw new RuntimeException(new ConfigNotFoundException(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId()));
              }

              final var connectionConfig =
                  statefulSplitSecrets(source.getWorkspaceId(), source.getConfiguration(), sourceDefIdToSpec.get(source.getSourceDefinitionId()));

              return source.withConfiguration(connectionConfig);
            });
        augmentedMap.put(ConfigSchema.SOURCE_CONNECTION, augmentedValue);
      }

      if (augmentedMap.containsKey(ConfigSchema.DESTINATION_CONNECTION)) {
        final Stream<?> augmentedValue = augmentedMap.get(ConfigSchema.DESTINATION_CONNECTION)
            .map(config -> {
              final DestinationConnection destination = (DestinationConnection) config;

              if (!destinationDefIdToSpec.containsKey(destination.getDestinationDefinitionId())) {
                throw new RuntimeException(
                    new ConfigNotFoundException(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId()));
              }

              final var connectionConfig = statefulSplitSecrets(destination.getWorkspaceId(), destination.getConfiguration(),
                  destinationDefIdToSpec.get(destination.getDestinationDefinitionId()));

              return destination.withConfiguration(connectionConfig);
            });
        augmentedMap.put(ConfigSchema.DESTINATION_CONNECTION, augmentedValue);
      }

      persistence.replaceAllConfigs(augmentedMap, dryRun);
    } else {
      persistence.replaceAllConfigs(configs, dryRun);
    }
  }

  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final var map = new HashMap<>(persistence.dumpConfigs());
    final var sourceKey = ConfigSchema.SOURCE_CONNECTION.name();
    final var destinationKey = ConfigSchema.DESTINATION_CONNECTION.name();

    if (map.containsKey(sourceKey)) {
      final Stream<JsonNode> augmentedValue = map.get(sourceKey).map(secretsHydrator::hydrate);
      map.put(sourceKey, augmentedValue);
    }

    if (map.containsKey(destinationKey)) {
      final Stream<JsonNode> augmentedValue = map.get(destinationKey).map(secretsHydrator::hydrate);
      map.put(destinationKey, augmentedValue);
    }

    return map;
  }

  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    persistence.loadData(seedPersistence);
  }

  public void setSpecFetcher(final Function<String, ConnectorSpecification> specFetcherFn) {
    this.specFetcherFn = specFetcherFn;
  }

}
