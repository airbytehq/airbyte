/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpers;
import io.airbyte.config.persistence.split_secrets.SplitSecretConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class takes secrets as arguments but never returns an secrets (even the ones that are passed
 * in as arguments).
 */
@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public class SecretsRepositoryWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsRepositoryWriter.class);

  private static final UUID NO_WORKSPACE = UUID.fromString("00000000-0000-0000-0000-000000000000");

  // private final ConfigPersistence persistence;
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator validator;
  private final Optional<SecretPersistence> longLivedSecretPersistence;
  private final Optional<SecretPersistence> ephemeralSecretPersistence;

  public SecretsRepositoryWriter(final ConfigRepository configRepository,
                                 final Optional<SecretPersistence> longLivedSecretPersistence,
                                 final Optional<SecretPersistence> ephemeralSecretPersistence) {
    this(configRepository, new JsonSchemaValidator(), longLivedSecretPersistence, ephemeralSecretPersistence);
  }

  @VisibleForTesting
  SecretsRepositoryWriter(final ConfigRepository configRepository,
                          final JsonSchemaValidator validator,
                          final Optional<SecretPersistence> longLivedSecretPersistence,
                          final Optional<SecretPersistence> ephemeralSecretPersistence) {
    this.configRepository = configRepository;
    this.validator = validator;
    this.longLivedSecretPersistence = longLivedSecretPersistence;
    this.ephemeralSecretPersistence = ephemeralSecretPersistence;
  }

  private Optional<SourceConnection> getOptionalSourceConnection(final UUID sourceId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getSourceConnection(sourceId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  // validates too!
  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {

    final var previousSourceConnection = getOptionalSourceConnection(source.getSourceId())
        .map(SourceConnection::getConfiguration);

    // strip secrets
    final JsonNode partialConfig = statefulUpdateSecrets(
        source.getWorkspaceId(),
        previousSourceConnection,
        source.getConfiguration(),
        connectorSpecification);
    final SourceConnection partialSource = Jsons.clone(source).withConfiguration(partialConfig);

    // validate partial to avoid secret leak issues.
    validator.ensure(connectorSpecification.getConnectionSpecification(), partialSource.getConfiguration());

    configRepository.writeSourceConnection(partialSource);
  }

  private Optional<DestinationConnection> getOptionalDestinationConnection(final UUID destinationId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getDestinationConnection(destinationId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeDestinationConnection(final DestinationConnection destination, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    final var previousDestinationConnection = getOptionalDestinationConnection(destination.getDestinationId())
        .map(DestinationConnection::getConfiguration);

    final JsonNode partialConfig = statefulUpdateSecrets(
        destination.getWorkspaceId(),
        previousDestinationConnection,
        destination.getConfiguration(),
        connectorSpecification);
    final DestinationConnection partialDestination = Jsons.clone(destination).withConfiguration(partialConfig);

    // validate partial to avoid secret leak issues.
    validator.ensure(connectorSpecification.getConnectionSpecification(), partialDestination.getConfiguration());

    configRepository.writeDestinationConnection(partialDestination);
  }

  /**
   * Detects secrets in the configuration. Writes them to the secrets store. It returns the config
   * stripped of secrets (replaced with pointers to the secrets store).
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

  /**
   * Converts between a dumpConfig() output and a replaceAllConfigs() input, by deserializing the
   * string/jsonnode into the AirbyteConfig, Stream&lt;Object&lt;AirbyteConfig.getClassName()&gt;&gt;
   *
   * @param configurations from dumpConfig()
   * @return input suitable for replaceAllConfigs()
   */
  public static Map<AirbyteConfig, Stream<?>> deserialize(final Map<String, Stream<JsonNode>> configurations) {
    final Map<AirbyteConfig, Stream<?>> deserialized = new LinkedHashMap<AirbyteConfig, Stream<?>>();
    for (final String configSchemaName : configurations.keySet()) {
      deserialized.put(
          ConfigSchema.valueOf(configSchemaName),
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
          .collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId, StandardSourceDefinition::getSpec));

      // get all destination defs so that we can use their specs when storing secrets.
      @SuppressWarnings("unchecked")
      final List<StandardDestinationDefinition> destinationDefs =
          (List<StandardDestinationDefinition>) augmentedMap.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION).collect(Collectors.toList());
      augmentedMap.put(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationDefs.stream());
      final Map<UUID, ConnectorSpecification> destinationDefIdToSpec = destinationDefs
          .stream()
          .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId, StandardDestinationDefinition::getSpec));

      if (augmentedMap.containsKey(ConfigSchema.SOURCE_CONNECTION)) {
        final Stream<?> augmentedValue = augmentedMap.get(ConfigSchema.SOURCE_CONNECTION)
            .map(config -> {
              final SourceConnection source = (SourceConnection) config;

              if (!sourceDefIdToSpec.containsKey(source.getSourceDefinitionId())) {
                throw new RuntimeException(new ConfigNotFoundException(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId()));
              }

              final var partialConfig = statefulSplitSecrets(
                  source.getWorkspaceId(),
                  source.getConfiguration(),
                  sourceDefIdToSpec.get(source.getSourceDefinitionId()));

              return source.withConfiguration(partialConfig);
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

              final var partialConfig = statefulSplitSecrets(
                  destination.getWorkspaceId(),
                  destination.getConfiguration(),
                  destinationDefIdToSpec.get(destination.getDestinationDefinitionId()));

              return destination.withConfiguration(partialConfig);
            });
        augmentedMap.put(ConfigSchema.DESTINATION_CONNECTION, augmentedValue);
      }

      configRepository.replaceAllConfigs1(augmentedMap, dryRun);
    } else {
      configRepository.replaceAllConfigs1(configs, dryRun);
    }
  }

  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    configRepository.loadData1(seedPersistence);
  }

}
