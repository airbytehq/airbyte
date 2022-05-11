/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.bootloader.SecretMigrator.ConnectorConfiguration;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.split_secrets.SecretCoordinate;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class SecretMigratorTest {

  private final UUID workspaceId = UUID.randomUUID();

  @Mock
  private ConfigPersistence configPersistence;

  @Mock
  private SecretPersistence secretPersistence;

  @Mock
  private JobPersistence jobPersistence;

  private SecretMigrator secretMigrator;

  @BeforeEach
  void setup() {
    secretMigrator = Mockito.spy(new SecretMigrator(configPersistence, jobPersistence, Optional.of(secretPersistence)));
  }

  @Test
  public void testMigrateSecret() throws JsonValidationException, IOException {
    final JsonNode sourceSpec = Jsons.jsonNode("sourceSpec");
    final UUID sourceDefinitionId = UUID.randomUUID();
    final StandardSourceDefinition standardSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(sourceDefinitionId)
        .withSpec(
            new ConnectorSpecification()
                .withConnectionSpecification(sourceSpec));
    final Map<UUID, JsonNode> standardSourceDefinitions = new HashMap<>();
    standardSourceDefinitions.put(sourceDefinitionId, standardSourceDefinition.getSpec().getConnectionSpecification());
    Mockito.when(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(Lists.newArrayList(standardSourceDefinition));

    final JsonNode sourceConfiguration = Jsons.jsonNode("sourceConfiguration");
    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefinitionId)
        .withConfiguration(sourceConfiguration)
        .withWorkspaceId(workspaceId);
    final List<SourceConnection> sourceConnections = Lists.newArrayList(sourceConnection);
    Mockito.when(configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class))
        .thenReturn(sourceConnections);

    final JsonNode destinationSpec = Jsons.jsonNode("destinationSpec");
    final UUID destinationDefinitionId = UUID.randomUUID();
    final StandardDestinationDefinition standardDestinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(destinationDefinitionId)
        .withSpec(
            new ConnectorSpecification()
                .withConnectionSpecification(destinationSpec));
    final Map<UUID, JsonNode> standardDestinationDefinitions = new HashMap<>();
    standardDestinationDefinitions.put(destinationDefinitionId, standardDestinationDefinition.getSpec().getConnectionSpecification());
    Mockito.when(configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(Lists.newArrayList(standardDestinationDefinition));

    final JsonNode destinationConfiguration = Jsons.jsonNode("destinationConfiguration");
    final DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destinationDefinitionId)
        .withConfiguration(destinationConfiguration)
        .withWorkspaceId(workspaceId);
    final List<DestinationConnection> destinationConnections = Lists.newArrayList(destinationConnection);
    Mockito.when(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class))
        .thenReturn(destinationConnections);

    // Mockito.doNothing().when(secretMigrator).migrateDestinations(Mockito.any(), Mockito.any());

    final String path = "Mocked static call source";
    Mockito.doReturn(Lists.newArrayList(path)).when(secretMigrator).getSecretPath(sourceSpec);
    Mockito.doReturn(Lists.newArrayList(path)).when(secretMigrator).getAllExplodedPath(sourceConfiguration, path);
    final String sourceSecret = "sourceSecret";
    Mockito.doReturn(Optional.of(Jsons.jsonNode(sourceSecret))).when(secretMigrator).getValueForPath(sourceConfiguration, path);
    Mockito.doReturn(Lists.newArrayList(path)).when(secretMigrator).getSecretPath(destinationSpec);
    Mockito.doReturn(Lists.newArrayList(path)).when(secretMigrator).getAllExplodedPath(destinationConfiguration, path);
    final String destinationSecret = "destinationSecret";
    Mockito.doReturn(Optional.of(Jsons.jsonNode(destinationSecret))).when(secretMigrator).getValueForPath(destinationConfiguration, path);

    Mockito.doReturn(Jsons.jsonNode("sanitized")).when(secretMigrator).replaceAtJsonNode(Mockito.any(), Mockito.any(), Mockito.any());
    secretMigrator.migrateSecrets();

    Mockito.verify(secretMigrator).migrateSources(sourceConnections, standardSourceDefinitions);
    Mockito.verify(secretPersistence).write(Mockito.any(), Mockito.eq(sourceSecret));
    secretPersistence.write(Mockito.any(), Mockito.any());
    Mockito.verify(secretMigrator).migrateDestinations(destinationConnections, standardDestinationDefinitions);
    Mockito.verify(secretPersistence).write(Mockito.any(), Mockito.eq(destinationSecret));

    Mockito.verify(jobPersistence).setSecretMigrationDone();
  }

  @Test
  void testSourceMigration() throws JsonValidationException, IOException {
    final UUID definitionId1 = UUID.randomUUID();
    final UUID definitionId2 = UUID.randomUUID();
    final UUID sourceId1 = UUID.randomUUID();
    final UUID sourceId2 = UUID.randomUUID();
    final JsonNode sourceConfiguration1 = Jsons.jsonNode("conf1");
    final JsonNode sourceConfiguration2 = Jsons.jsonNode("conf2");
    final JsonNode sourceDefinition1 = Jsons.jsonNode("def1");
    final JsonNode sourceDefinition2 = Jsons.jsonNode("def2");
    final SourceConnection sourceConnection1 = new SourceConnection()
        .withSourceId(sourceId1)
        .withSourceDefinitionId(definitionId1)
        .withConfiguration(sourceConfiguration1);
    final SourceConnection sourceConnection2 = new SourceConnection()
        .withSourceId(sourceId2)
        .withSourceDefinitionId(definitionId2)
        .withConfiguration(sourceConfiguration2);

    final List<SourceConnection> sources = Lists.newArrayList(sourceConnection1, sourceConnection2);
    final Map<UUID, JsonNode> definitionIdToDestinationSpecs = new HashMap<>();
    definitionIdToDestinationSpecs.put(definitionId1, sourceDefinition1);
    definitionIdToDestinationSpecs.put(definitionId2, sourceDefinition2);

    Mockito.doReturn(Jsons.emptyObject()).when(secretMigrator).migrateConfiguration(
        Mockito.any(),
        Mockito.any());

    secretMigrator.migrateSources(sources, definitionIdToDestinationSpecs);

    Mockito.verify(configPersistence).writeConfig(ConfigSchema.SOURCE_CONNECTION, sourceId1.toString(), sourceConnection1);
    Mockito.verify(configPersistence).writeConfig(ConfigSchema.SOURCE_CONNECTION, sourceId2.toString(), sourceConnection2);
  }

  @Test
  void testDestinationMigration() throws JsonValidationException, IOException {
    final UUID definitionId1 = UUID.randomUUID();
    final UUID definitionId2 = UUID.randomUUID();
    final UUID destinationId1 = UUID.randomUUID();
    final UUID destinationId2 = UUID.randomUUID();
    final JsonNode destinationConfiguration1 = Jsons.jsonNode("conf1");
    final JsonNode destinationConfiguration2 = Jsons.jsonNode("conf2");
    final JsonNode destinationDefinition1 = Jsons.jsonNode("def1");
    final JsonNode destinationDefinition2 = Jsons.jsonNode("def2");
    final DestinationConnection destinationConnection1 = new DestinationConnection()
        .withDestinationId(destinationId1)
        .withDestinationDefinitionId(definitionId1)
        .withConfiguration(destinationConfiguration1);
    final DestinationConnection destinationConnection2 = new DestinationConnection()
        .withDestinationId(destinationId2)
        .withDestinationDefinitionId(definitionId2)
        .withConfiguration(destinationConfiguration2);

    final List<DestinationConnection> destinations = Lists.newArrayList(destinationConnection1, destinationConnection2);
    final Map<UUID, JsonNode> definitionIdToDestinationSpecs = new HashMap<>();
    definitionIdToDestinationSpecs.put(definitionId1, destinationDefinition1);
    definitionIdToDestinationSpecs.put(definitionId2, destinationDefinition2);

    Mockito.doReturn(Jsons.emptyObject()).when(secretMigrator).migrateConfiguration(
        Mockito.any(),
        Mockito.any());

    secretMigrator.migrateDestinations(destinations, definitionIdToDestinationSpecs);

    Mockito.verify(configPersistence).writeConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId1.toString(), destinationConnection1);
    Mockito.verify(configPersistence).writeConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId2.toString(), destinationConnection2);
  }

  @Test
  void testMigrateConfigurationWithoutSpecs() {
    final ConnectorConfiguration connectorConfiguration = new ConnectorConfiguration(null, null, null);

    Assertions.assertThrows(IllegalStateException.class, () -> secretMigrator.migrateConfiguration(connectorConfiguration, null));
  }

  @Test
  void testMissingSecret() {
    final List<String> secretPathList = Lists.newArrayList("secretPath");

    Mockito.doReturn(secretPathList).when(secretMigrator).getSecretPath(Mockito.any());
    Mockito.doReturn(secretPathList).when(secretMigrator).getAllExplodedPath(Mockito.any(), Mockito.eq(secretPathList.get(0)));
    Mockito.doReturn(Optional.empty()).when(secretMigrator).getValueForPath(Mockito.any(), Mockito.eq(secretPathList.get(0)));

    final ConnectorConfiguration connectorConfiguration = new ConnectorConfiguration(UUID.randomUUID(), Jsons.emptyObject(), Jsons.emptyObject());
    Assertions.assertThrows(IllegalStateException.class, () -> secretMigrator.migrateConfiguration(connectorConfiguration, () -> UUID.randomUUID()));
  }

  @Test
  void testMigrateConfiguration() {
    final List<String> secretPathList = Lists.newArrayList("$.secretPath");

    Mockito.doReturn(secretPathList).when(secretMigrator).getSecretPath(Mockito.any());
    Mockito.doReturn(secretPathList).when(secretMigrator).getAllExplodedPath(Mockito.any(), Mockito.eq(secretPathList.get(0)));
    Mockito.doReturn(Optional.of(Jsons.jsonNode(secretPathList.get(0)))).when(secretMigrator).getValueForPath(Mockito.any(),
        Mockito.eq(secretPathList.get(0)));

    final ConnectorConfiguration connectorConfiguration = new ConnectorConfiguration(UUID.randomUUID(), Jsons.emptyObject(), Jsons.emptyObject());

    secretMigrator.migrateConfiguration(connectorConfiguration, () -> UUID.randomUUID());
    Mockito.verify(secretPersistence).write(Mockito.any(), Mockito.any());
  }

  @Test
  void testMigrateConfigurationAlreadyInSecretManager() {
    final List<String> secretPathList = Lists.newArrayList("$.secretPath");

    Mockito.doReturn(secretPathList).when(secretMigrator).getSecretPath(Mockito.any());
    Mockito.doReturn(secretPathList).when(secretMigrator).getAllExplodedPath(Mockito.any(), Mockito.eq(secretPathList.get(0)));

    final SecretCoordinate fakeCoordinate = new SecretCoordinate("fake", 1);
    Mockito.doReturn(Optional.of(Jsons.jsonNode(fakeCoordinate))).when(secretMigrator).getValueForPath(Mockito.any(),
        Mockito.eq(secretPathList.get(0)));

    final ConnectorConfiguration connectorConfiguration = new ConnectorConfiguration(UUID.randomUUID(), Jsons.emptyObject(), Jsons.emptyObject());

    secretMigrator.migrateConfiguration(connectorConfiguration, () -> UUID.randomUUID());
    Mockito.verify(secretPersistence, Mockito.times(0)).write(Mockito.any(), Mockito.any());
  }

}
