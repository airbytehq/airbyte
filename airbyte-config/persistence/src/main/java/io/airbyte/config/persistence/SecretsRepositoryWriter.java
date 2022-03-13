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
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class takes secrets as arguments but never returns a secrets as return values (even the ones
 * that are passed in as arguments). It is responsible for writing connector secrets to the correct
 * secrets store and then making sure the remainder of the configuration is written to the Config
 * Database.
 */
@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public class SecretsRepositoryWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(SecretsRepositoryWriter.class);

  private static final UUID NO_WORKSPACE = UUID.fromString("00000000-0000-0000-0000-000000000000");

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

  private Optional<SourceConnection> getSourceIfExists(final UUID sourceId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getSourceConnection(sourceId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  // validates too!
  public void writeSourceConnection(final SourceConnection source, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    final var previousSourceConnection = getSourceIfExists(source.getSourceId())
        .map(SourceConnection::getConfiguration);

    // strip secrets
    final JsonNode partialConfig = statefulUpdateSecrets(
        source.getWorkspaceId(),
        previousSourceConnection,
        source.getConfiguration(),
        connectorSpecification);
    final SourceConnection partialSource = Jsons.clone(source).withConfiguration(partialConfig);

    configRepository.writeSourceConnectionNoSecrets(partialSource);
  }

  private Optional<DestinationConnection> getDestinationIfExists(final UUID destinationId) throws JsonValidationException, IOException {
    try {
      return Optional.of(configRepository.getDestinationConnection(destinationId));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    }
  }

  public void writeDestinationConnection(final DestinationConnection destination, final ConnectorSpecification connectorSpecification)
      throws JsonValidationException, IOException {
    final var previousDestinationConnection = getDestinationIfExists(destination.getDestinationId())
        .map(DestinationConnection::getConfiguration);

    final JsonNode partialConfig = statefulUpdateSecrets(
        destination.getWorkspaceId(),
        previousDestinationConnection,
        destination.getConfiguration(),
        connectorSpecification);
    final DestinationConnection partialDestination = Jsons.clone(destination).withConfiguration(partialConfig);

    configRepository.writeDestinationConnectionNoSecrets(partialDestination);
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
  private JsonNode statefulSplitSecrets(final UUID workspaceId, final JsonNode fullConfig, final ConnectorSpecification spec) {
    return splitSecretConfig(workspaceId, fullConfig, spec, longLivedSecretPersistence);
  }

  // todo (cgardens) - the contract on this method is hard to follow, because it sometimes returns
  // secrets (i.e. when there is no longLivedSecretPersistence). If we treated all secrets the same
  // (i.e. used a separate db for secrets when the user didn't provide a store), this would be easier
  // to reason about.
  /**
   * If a secrets store is present, this method attempts to fetch the existing config and merge its
   * secrets with the passed in config. If there is no secrets store, it just returns the passed in
   * config. Also validates the config.
   *
   * @param workspaceId workspace id for the config
   * @param oldConfig old full config
   * @param fullConfig new full config
   * @param spec connector specification
   * @return partial config
   */
  private JsonNode statefulUpdateSecrets(final UUID workspaceId,
                                         final Optional<JsonNode> oldConfig,
                                         final JsonNode fullConfig,
                                         final ConnectorSpecification spec)
      throws JsonValidationException {
    validator.ensure(spec.getConnectionSpecification(), fullConfig);

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

      configRepository.replaceAllConfigsNoSecrets(augmentedMap, dryRun);
    } else {
      configRepository.replaceAllConfigsNoSecrets(configs, dryRun);
    }
  }

}
