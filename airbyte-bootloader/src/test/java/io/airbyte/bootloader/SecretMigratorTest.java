/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class SecretMigratorTest {

  private final UUID workspaceId = UUID.randomUUID();

  @Mock
  private ConfigRepository configRepository;

  @Mock
  private SecretsRepositoryReader secretsReader;

  @Mock
  private SecretsRepositoryWriter secretsWriter;

  @Mock
  private SecretPersistence secretPersistence;

  @Mock
  private JobPersistence jobPersistence;

  private SecretMigrator secretMigrator;

  @BeforeEach
  void setup() {
    secretMigrator = Mockito.spy(new SecretMigrator(secretsReader, secretsWriter, configRepository, jobPersistence, Optional.of(secretPersistence)));
  }

  @Test
  void testMigrateSecret() throws Exception {
    final JsonNode sourceSpec = Jsons.jsonNode("sourceSpec");
    final UUID sourceDefinitionId = UUID.randomUUID();
    final StandardSourceDefinition standardSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(sourceDefinitionId)
        .withSpec(
            new ConnectorSpecification()
                .withConnectionSpecification(sourceSpec));
    final Map<UUID, ConnectorSpecification> standardSourceDefinitions = new HashMap<>();
    standardSourceDefinitions.put(sourceDefinitionId, standardSourceDefinition.getSpec());
    when(configRepository.listStandardSourceDefinitions(true))
        .thenReturn(Lists.newArrayList(standardSourceDefinition));

    final JsonNode sourceConfiguration = Jsons.jsonNode("sourceConfiguration");
    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefinitionId)
        .withConfiguration(sourceConfiguration)
        .withWorkspaceId(workspaceId);
    final List<SourceConnection> sourceConnections = Lists.newArrayList(sourceConnection);
    when(configRepository.listSourceConnection())
        .thenReturn(sourceConnections);

    final JsonNode destinationSpec = Jsons.jsonNode("destinationSpec");
    final UUID destinationDefinitionId = UUID.randomUUID();
    final StandardDestinationDefinition standardDestinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(destinationDefinitionId)
        .withSpec(
            new ConnectorSpecification()
                .withConnectionSpecification(destinationSpec));
    final Map<UUID, ConnectorSpecification> standardDestinationDefinitions = new HashMap<>();
    standardDestinationDefinitions.put(destinationDefinitionId, standardDestinationDefinition.getSpec());
    when(configRepository.listStandardDestinationDefinitions(true))
        .thenReturn(Lists.newArrayList(standardDestinationDefinition));

    final JsonNode destinationConfiguration = Jsons.jsonNode("destinationConfiguration");
    final DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destinationDefinitionId)
        .withConfiguration(destinationConfiguration)
        .withWorkspaceId(workspaceId);
    final List<DestinationConnection> destinationConnections = Lists.newArrayList(destinationConnection);
    when(configRepository.listDestinationConnection())
        .thenReturn(destinationConnections);

    when(secretsReader.getSourceConnectionWithSecrets(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(secretsReader.getDestinationConnectionWithSecrets(destinationConnection.getDestinationId())).thenReturn(destinationConnection);

    secretMigrator.migrateSecrets();

    Mockito.verify(secretMigrator).migrateSources(sourceConnections, standardSourceDefinitions);
    Mockito.verify(secretsWriter).writeSourceConnection(sourceConnection, standardSourceDefinition.getSpec());
    secretPersistence.write(any(), any());
    Mockito.verify(secretMigrator).migrateDestinations(destinationConnections, standardDestinationDefinitions);
    Mockito.verify(secretsWriter).writeDestinationConnection(destinationConnection, standardDestinationDefinition.getSpec());

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
    final ConnectorSpecification sourceDefinition1 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode("def1"));
    final ConnectorSpecification sourceDefinition2 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode("def2"));
    final SourceConnection sourceConnection1 = new SourceConnection()
        .withSourceId(sourceId1)
        .withSourceDefinitionId(definitionId1)
        .withConfiguration(sourceConfiguration1);
    final SourceConnection sourceConnection2 = new SourceConnection()
        .withSourceId(sourceId2)
        .withSourceDefinitionId(definitionId2)
        .withConfiguration(sourceConfiguration2);

    final List<SourceConnection> sources = Lists.newArrayList(sourceConnection1, sourceConnection2);
    final Map<UUID, ConnectorSpecification> definitionIdToDestinationSpecs = new HashMap<>();
    definitionIdToDestinationSpecs.put(definitionId1, sourceDefinition1);
    definitionIdToDestinationSpecs.put(definitionId2, sourceDefinition2);

    secretMigrator.migrateSources(sources, definitionIdToDestinationSpecs);

    Mockito.verify(secretsWriter).writeSourceConnection(sourceConnection1, sourceDefinition1);
    Mockito.verify(secretsWriter).writeSourceConnection(sourceConnection2, sourceDefinition2);
  }

  @Test
  void testDestinationMigration() throws JsonValidationException, IOException {
    final UUID definitionId1 = UUID.randomUUID();
    final UUID definitionId2 = UUID.randomUUID();
    final UUID destinationId1 = UUID.randomUUID();
    final UUID destinationId2 = UUID.randomUUID();
    final JsonNode destinationConfiguration1 = Jsons.jsonNode("conf1");
    final JsonNode destinationConfiguration2 = Jsons.jsonNode("conf2");
    final ConnectorSpecification destinationDefinition1 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode("def1"));
    final ConnectorSpecification destinationDefinition2 = new ConnectorSpecification().withConnectionSpecification(Jsons.jsonNode("def2"));
    final DestinationConnection destinationConnection1 = new DestinationConnection()
        .withDestinationId(destinationId1)
        .withDestinationDefinitionId(definitionId1)
        .withConfiguration(destinationConfiguration1);
    final DestinationConnection destinationConnection2 = new DestinationConnection()
        .withDestinationId(destinationId2)
        .withDestinationDefinitionId(definitionId2)
        .withConfiguration(destinationConfiguration2);

    final List<DestinationConnection> destinations = Lists.newArrayList(destinationConnection1, destinationConnection2);
    final Map<UUID, ConnectorSpecification> definitionIdToDestinationSpecs = new HashMap<>();
    definitionIdToDestinationSpecs.put(definitionId1, destinationDefinition1);
    definitionIdToDestinationSpecs.put(definitionId2, destinationDefinition2);

    secretMigrator.migrateDestinations(destinations, definitionIdToDestinationSpecs);

    Mockito.verify(secretsWriter).writeDestinationConnection(destinationConnection1, destinationDefinition1);
    Mockito.verify(secretsWriter).writeDestinationConnection(destinationConnection2, destinationDefinition2);
  }

}
