/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

public class ConfigQueries {

  public static void deleteSourceDefinition(final ConfigPersistence configPersistence, final UUID sourceDefinitionId) throws Exception {
    deleteConnectorDefinition(
        configPersistence,
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        ConfigSchema.SOURCE_CONNECTION,
        SourceConnection.class,
        SourceConnection::getSourceDefinitionId,
        sourceDefinitionId);
  }

  public static void deleteDestinationDefinition(final ConfigPersistence configPersistence, final UUID destinationDefinitionId) throws Exception {
    deleteConnectorDefinition(
        configPersistence,
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        ConfigSchema.DESTINATION_CONNECTION,
        DestinationConnection.class,
        DestinationConnection::getDestinationDefinitionId,
        destinationDefinitionId);
  }

  private static <T> void deleteConnectorDefinition(
                                                    final ConfigPersistence configPersistence,
                                                    final ConfigSchema definitionType,
                                                    final ConfigSchema connectorType,
                                                    final Class<T> connectorClass,
                                                    final Function<T, UUID> connectorDefinitionIdGetter,
                                                    final UUID definitionId)
      throws Exception {
    final Set<T> connectors = configPersistence.listConfigs(connectorType, connectorClass)
        .stream()
        .filter(connector -> connectorDefinitionIdGetter.apply(connector).equals(definitionId))
        .collect(Collectors.toSet());
    for (final T connector : connectors) {
      final Set<StandardSync> syncs = configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)
          .stream()
          .filter(sync -> sync.getDestinationId().equals(connectorDefinitionIdGetter.apply(connector)))
          .collect(Collectors.toSet());

      for (final StandardSync sync : syncs) {
        configPersistence.deleteConfig(ConfigSchema.STANDARD_SYNC, sync.getConnectionId().toString());
      }
      configPersistence.deleteConfig(connectorType, connectorDefinitionIdGetter.apply(connector).toString());
    }
    configPersistence.deleteConfig(definitionType, definitionId.toString());
  }

}
