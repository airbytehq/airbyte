/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static io.airbyte.config.persistence.split_secrets.SecretsHelpers.COORDINATE_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.JsonPaths;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHelpers;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class SecretMigrator {

  private final ConfigPersistence configPersistence;
  private final JobPersistence jobPersistence;
  private final Optional<SecretPersistence> secretPersistence;

  @Value
  static class ConnectorConfiguration {

    private final UUID workspace;
    private final JsonNode configuration;
    private final JsonNode spec;

  }

  /**
   * Perform a secret migration. It will load all the actor specs extract the secret JsonPath from it.
   * Then for all the secret that are stored in a plain text format, it will save the plain text in
   * the secret manager and store the coordinate in the config DB.
   */
  public void migrateSecrets() throws JsonValidationException, IOException {
    if (secretPersistence.isEmpty()) {
      log.info("No secret persistence is provided, the migration won't be run ");

      return;
    }
    final List<StandardSourceDefinition> standardSourceDefinitions =
        configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);

    final Map<UUID, JsonNode> definitionIdToSourceSpecs = standardSourceDefinitions
        .stream().collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId,
            def -> def.getSpec().getConnectionSpecification()));

    final List<SourceConnection> sources = configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);

    migrateSources(sources, definitionIdToSourceSpecs);

    final List<StandardDestinationDefinition> standardDestinationDefinitions =
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION,
            StandardDestinationDefinition.class);

    final Map<UUID, JsonNode> definitionIdToDestinationSpecs = standardDestinationDefinitions.stream()
        .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId,
            def -> def.getSpec().getConnectionSpecification()));

    final List<DestinationConnection> destinations = configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);

    migrateDestinations(destinations, definitionIdToDestinationSpecs);

    jobPersistence.setSecretMigrationDone();
  }

  /**
   * This is migrating the secrets for the source actors
   */
  @VisibleForTesting
  void migrateSources(final List<SourceConnection> sources, final Map<UUID, JsonNode> definitionIdToSourceSpecs)
      throws JsonValidationException, IOException {
    log.info("Migrating Sources");
    final List<SourceConnection> sourceConnections = sources.stream()
        .map(source -> {
          final JsonNode migratedConfig = migrateConfiguration(new ConnectorConfiguration(
              source.getWorkspaceId(),
              source.getConfiguration(),
              definitionIdToSourceSpecs.get(source.getSourceDefinitionId())),
              () -> UUID.randomUUID());
          source.setConfiguration(migratedConfig);
          return source;
        })
        .toList();

    for (final SourceConnection source : sourceConnections) {
      configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), source);
    }
  }

  /**
   * This is migrating the secrets for the destination actors
   */
  @VisibleForTesting
  void migrateDestinations(final List<DestinationConnection> destinations, final Map<UUID, JsonNode> definitionIdToDestinationSpecs)
      throws JsonValidationException, IOException {
    log.info("Migration Destinations");

    final List<DestinationConnection> destinationConnections = destinations.stream().map(destination -> {
      final JsonNode migratedConfig = migrateConfiguration(new ConnectorConfiguration(
          destination.getWorkspaceId(),
          destination.getConfiguration(),
          definitionIdToDestinationSpecs.get(destination.getDestinationDefinitionId())),
          () -> UUID.randomUUID());
      destination.setConfiguration(migratedConfig);
      return destination;
    })
        .toList();
    for (final DestinationConnection destination : destinationConnections) {
      configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, destination.getDestinationId().toString(), destination);
    }
  }

  /**
   * This is a generic method to migrate an actor configuration It will extract the secret path form
   * the provided spec and then replace them by coordinates in the actor configuration
   */
  @VisibleForTesting
  JsonNode migrateConfiguration(final ConnectorConfiguration connectorConfiguration, final Supplier<UUID> uuidProvider) {
    if (connectorConfiguration.getSpec() == null) {
      throw new IllegalStateException("No connector definition to match the connector");
    }

    final AtomicReference<JsonNode> connectorConfigurationJson = new AtomicReference<>(connectorConfiguration.getConfiguration());
    final List<String> uniqSecretPaths = getSecretPath(connectorConfiguration.getSpec())
        .stream()
        .flatMap(secretPath -> getAllExplodedPath(connectorConfigurationJson.get(), secretPath).stream())
        .toList();

    final UUID workspaceId = connectorConfiguration.getWorkspace();
    uniqSecretPaths.forEach(secretPath -> {
      final Optional<JsonNode> secretValue = getValueForPath(connectorConfigurationJson.get(), secretPath);
      if (secretValue.isEmpty()) {
        throw new IllegalStateException("Missing secret for the path: " + secretPath);
      }

      // Only migrate plain text.
      if (secretValue.get().isTextual()) {
        final JsonNode stringSecretValue = secretValue.get();

        final SecretCoordinate coordinate =
            new SecretCoordinate(SecretsHelpers.getCoordinatorBase("airbyte_workspace_", workspaceId, uuidProvider), 1);
        secretPersistence.get().write(coordinate, stringSecretValue.textValue());
        connectorConfigurationJson.set(replaceAtJsonNode(connectorConfigurationJson.get(), secretPath,
            Jsons.jsonNode(Map.of(COORDINATE_FIELD, coordinate.getFullCoordinate()))));
      } else {
        log.error("Not migrating already migrated secrets");
      }

    });

    return connectorConfigurationJson.get();
  }

  /**
   * Wrapper to help to mock static methods
   */
  @VisibleForTesting
  JsonNode replaceAtJsonNode(final JsonNode connectorConfigurationJson, final String secretPath, final JsonNode replacement) {
    return JsonPaths.replaceAtJsonNode(connectorConfigurationJson, secretPath, replacement);
  }

  /**
   * Wrapper to help to mock static methods
   */
  @VisibleForTesting
  List<String> getSecretPath(final JsonNode specs) {
    return SecretsHelpers.getSortedSecretPaths(specs);
  }

  /**
   * Wrapper to help to mock static methods
   */
  @VisibleForTesting
  List<String> getAllExplodedPath(final JsonNode node, final String path) {
    return JsonPaths.getPaths(node, path);
  }

  /**
   * Wrapper to help to mock static methods
   */
  @VisibleForTesting
  Optional<JsonNode> getValueForPath(final JsonNode node, final String path) {
    return JsonPaths.getSingleValue(node, path);
  }

}
