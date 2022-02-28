/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class ConfigRepositoryE2EReadWriteTest {

  private final StandardWorkspace workspace = new StandardWorkspace()
      .withWorkspaceId(UUID.randomUUID())
      .withName("Default workspace")
      .withSlug("default-workspace")
      .withInitialSetupComplete(true);
  private static PostgreSQLContainer<?> container;
  private Database database;
  private ConfigRepository configRepository;
  private DatabaseConfigPersistence configPersistence;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @BeforeEach
  void setup() throws IOException, JsonValidationException {
    final var secretPersistence = new MemorySecretPersistence();
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));
    configRepository =
        spy(new ConfigRepository(configPersistence, new NoOpSecretsHydrator(), Optional.of(secretPersistence), Optional.of(secretPersistence),
            database));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, DatabaseConfigPersistenceLoadDataTest.class.getName());
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
    configRepository.writeStandardWorkspace(workspace);
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @Test
  void testWorkspaceCountConnections() throws IOException, JsonValidationException {

    assertEquals(0, configRepository.countConnectionsForWorkspace(workspace.getWorkspaceId()));
    assertEquals(0, configRepository.countDestinationsForWorkspace(workspace.getWorkspaceId()));
    assertEquals(0, configRepository.countSourcesForWorkspace(workspace.getWorkspaceId()));

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withSourceType(SourceType.DATABASE)
        .withDockerRepository("docker-repo")
        .withDockerImageTag("1.2.0")
        .withName("sourceDefinition");
    configRepository.writeStandardSourceDefinition(sourceDefinition);

    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withDockerRepository("docker-repo")
        .withDockerImageTag("1.4.0")
        .withName("destinationDefinition");
    configRepository.writeStandardDestinationDefinition(destinationDefinition);

    final int sourceCount = 3;
    for (int i = 0; i < sourceCount; i++) {
      final SourceConnection source = new SourceConnection()
          .withSourceDefinitionId(sourceDefinition.getSourceDefinitionId())
          .withSourceId(UUID.randomUUID())
          .withName("SomeConnector")
          .withWorkspaceId(workspace.getWorkspaceId())
          .withConfiguration(Jsons.deserialize("{}"));
      final ConnectorSpecification specification = new ConnectorSpecification()
          .withConnectionSpecification(Jsons.deserialize("{}"));
      configRepository.writeSourceConnection(source, specification);
    }

    final int destinationCount = 4;
    for (int i = 0; i < destinationCount; i++) {
      final DestinationConnection destination = new DestinationConnection()
          .withDestinationDefinitionId(destinationDefinition.getDestinationDefinitionId())
          .withDestinationId(UUID.randomUUID())
          .withName("SomeConnector")
          .withWorkspaceId(workspace.getWorkspaceId())
          .withConfiguration(Jsons.deserialize("{}"));
      final ConnectorSpecification specification = new ConnectorSpecification()
          .withConnectionSpecification(Jsons.deserialize("{}"));
      configRepository.writeDestinationConnection(destination, specification);
    }

    final int connectionCount = 0;

    assertEquals(connectionCount, configRepository.countConnectionsForWorkspace(workspace.getWorkspaceId()));
    assertEquals(destinationCount, configRepository.countDestinationsForWorkspace(workspace.getWorkspaceId()));
    assertEquals(sourceCount, configRepository.countSourcesForWorkspace(workspace.getWorkspaceId()));
  }

}
