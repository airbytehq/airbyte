/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static io.airbyte.config.persistence.split_secrets.SecretsHelpers.COORDINATE_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
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
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class SecretMigrator {

  private final ConfigPersistence configPersistence;
  private final SecretPersistence secretPersistence;

  @Value
  class ConnectorConfiguration {

    private final UUID workspace;
    private final JsonNode configuration;
    private final JsonNode specs;

  }

  void migrateSecrets() throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> standardSourceDefinitions = configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION,
        StandardSourceDefinition.class);

    final List<StandardDestinationDefinition> standardDestinationDefinitions =
        configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION,
            StandardDestinationDefinition.class);

    final Map<UUID, JsonNode> definitionIdToDestinationSpecs = standardDestinationDefinitions.stream()
        .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId,
            def -> def.getSpec().getConnectionSpecification()));

    final Map<UUID, JsonNode> definitionIdToSourceSpecs = standardSourceDefinitions
        .stream().collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId,
            def -> def.getSpec().getConnectionSpecification()));

    final List<SourceConnection> sources = configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);

    log.info("Migrating Sources");
    sources.stream()
        .map(source -> {
          final JsonNode migratedConfig = migrateConfiguration(new ConnectorConfiguration(
              source.getWorkspaceId(),
              source.getConfiguration(),
              definitionIdToSourceSpecs.get(source.getSourceDefinitionId())));
          source.setConfiguration(migratedConfig);
          return source;
        })
        .forEach(source -> {
          try {
            configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), source);
          } catch (final JsonValidationException e) {
            e.printStackTrace();
          } catch (final IOException e) {
            e.printStackTrace();
          }
        });

    final List<DestinationConnection> destinations = configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);

    log.info("Migration Destinations");
    destinations.stream().map(destination -> {
      final JsonNode migratedConfig = migrateConfiguration(new ConnectorConfiguration(
          destination.getWorkspaceId(),
          destination.getConfiguration(),
          definitionIdToDestinationSpecs.get(destination.getDestinationDefinitionId())));
      destination.setConfiguration(migratedConfig);
      return destination;
    })
        .forEach(destination -> {
          try {
            configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, destination.getDestinationId().toString(), destination);
          } catch (final JsonValidationException e) {
            e.printStackTrace();
          } catch (final IOException e) {
            e.printStackTrace();
          }
        });

  }

  private JsonNode migrateConfiguration(final ConnectorConfiguration connectorConfiguration) {
    if (connectorConfiguration.getSpecs() == null) {
      throw new IllegalStateException("No connector definition to match the connector");
    }

    final AtomicReference<JsonNode> connectorConfigurationJson = new AtomicReference<>(connectorConfiguration.getConfiguration());
    final List<String> uniqSecretPaths = SecretsHelpers.getSortedSecretPaths(connectorConfiguration.getSpecs())
        .stream().flatMap(secretPath -> JsonPaths.getPaths(connectorConfigurationJson.get(), secretPath).stream())
        .toList();

    final UUID workspaceId = connectorConfiguration.getWorkspace();
    uniqSecretPaths.forEach(secretPath -> {
      final Optional<JsonNode> secretValue = JsonPaths.getSingleValue(connectorConfigurationJson.get(), secretPath);
      if (secretValue.isEmpty()) {
        throw new IllegalStateException("Missing secret for the path: " + secretPath);
      }

      // Only migrate plain text.
      if (secretValue.get().isTextual()) {
        final JsonNode stringSecretValue = secretValue.get();

        final SecretCoordinate coordinate = new SecretCoordinate("airbyte_workspace_" + workspaceId + "_secret_" + UUID.randomUUID(), 1);
        secretPersistence.write(coordinate, stringSecretValue.textValue());
        connectorConfigurationJson.set(JsonPaths.replaceAtJsonNode(connectorConfigurationJson.get(), secretPath,
            Jsons.jsonNode(Map.of(COORDINATE_FIELD, coordinate.getFullCoordinate()))));
      } else {
        log.error("Not migrating already migrating secrets");
      }

    });

    return connectorConfigurationJson.get();
  }

}
