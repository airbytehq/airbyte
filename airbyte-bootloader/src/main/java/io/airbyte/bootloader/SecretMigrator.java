/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static io.airbyte.config.persistence.split_secrets.SecretsHelpers.COORDINATE_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.JsonPaths;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
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
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class SecretMigrator {

  private final ConfigPersistence configPersistence;
  private final SecretPersistence secretPersistence;

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

    log.error("Migration Sources");
    sources.forEach(source -> {
      final JsonNode spec = definitionIdToSourceSpecs.get(source.getSourceDefinitionId());
      if (spec == null) {
        throw new IllegalStateException("No source definition to match the source");
      }

      final AtomicReference<JsonNode> sourceConfiguration = new AtomicReference<>(source.getConfiguration());
      final List<String> uniqSecretPaths = SecretsHelpers.getSortedSecretPaths(spec)
          .stream().flatMap(secretPath -> JsonPaths.getPaths(sourceConfiguration.get(), secretPath).stream())
          .toList();

      final UUID workspaceId = source.getWorkspaceId();
      uniqSecretPaths.forEach(secretPath -> {
        log.error("Path: " + secretPath);
        final Optional<JsonNode> secretValue = JsonPaths.getSingleValue(sourceConfiguration.get(), secretPath);

        if (secretValue.isEmpty() || !secretValue.get().isTextual()) {
          throw new IllegalStateException();
        }

        final JsonNode stringSecretValue = secretValue.get();

        final SecretCoordinate coordinate = new SecretCoordinate("airbyte_workspace_" + workspaceId + "_secret_" + UUID.randomUUID(), 1);
        secretPersistence.write(coordinate, stringSecretValue.textValue());
        sourceConfiguration.set(JsonPaths.replaceAtJsonNode(sourceConfiguration.get(), secretPath,
            Jsons.jsonNode(Map.of(COORDINATE_FIELD, coordinate.getFullCoordinate()))));

      });
      source.setConfiguration(sourceConfiguration.get());
      try {
        configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, source.getSourceId().toString(), source);
      } catch (final JsonValidationException e) {
        e.printStackTrace();
      } catch (final IOException e) {
        e.printStackTrace();
      }
    });

  }

}
