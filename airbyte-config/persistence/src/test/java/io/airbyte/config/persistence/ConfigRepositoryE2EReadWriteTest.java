/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class ConfigRepositoryE2EReadWriteTest {

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
    for (final StandardWorkspace workspace : MockData.standardWorkspaces()) {
      configRepository.writeStandardWorkspace(workspace);
    }
    for (final StandardSourceDefinition sourceDefinition : MockData.standardSourceDefinitions()) {
      configRepository.writeStandardSourceDefinition(sourceDefinition);
    }
    for (final StandardDestinationDefinition destinationDefinition : MockData.standardDestinationDefinitions()) {
      configRepository.writeStandardDestinationDefinition(destinationDefinition);
    }
    final ConnectorSpecification specification = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.deserialize("{}"));
    for (final SourceConnection connection : MockData.sourceConnections()) {
      configRepository.writeSourceConnection(connection, specification);
    }
    for (final DestinationConnection connection : MockData.destinationConnections()) {
      configRepository.writeDestinationConnection(connection, specification);
    }
    for (final StandardSyncOperation operation : MockData.standardSyncOperations()) {
      configRepository.writeStandardSyncOperation(operation);
    }
    for (final StandardSync sync : MockData.standardSyncs()) {
      configRepository.writeStandardSync(sync);
    }
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @Test
  void testWorkspaceCountConnections() throws IOException {

    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    assertEquals(MockData.standardSyncs().size() - 1, configRepository.countConnectionsForWorkspace(workspaceId));
    assertEquals(MockData.destinationConnections().size() - 1, configRepository.countDestinationsForWorkspace(workspaceId));
    assertEquals(MockData.sourceConnections().size() - 1, configRepository.countSourcesForWorkspace(workspaceId));
  }

  @Test
  void testSimpleInsertActorCatalog() throws IOException, JsonValidationException, SQLException {

    final StandardWorkspace workspace = MockData.standardWorkspaces().get(0);

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withSourceType(SourceType.DATABASE)
        .withDockerRepository("docker-repo")
        .withDockerImageTag("1.2.0")
        .withName("sourceDefinition");
    configRepository.writeStandardSourceDefinition(sourceDefinition);

    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(sourceDefinition.getSourceDefinitionId())
        .withSourceId(UUID.randomUUID())
        .withName("SomeConnector")
        .withWorkspaceId(workspace.getWorkspaceId())
        .withConfiguration(Jsons.deserialize("{}"));
    final ConnectorSpecification specification = new ConnectorSpecification()
        .withConnectionSpecification(Jsons.deserialize("{}"));
    configRepository.writeSourceConnection(source, specification);

    final AirbyteCatalog actorCatalog = CatalogHelpers.createAirbyteCatalog("clothes", Field.of("name", JsonSchemaType.STRING));
    configRepository.writeActorCatalogFetchEvent(
        actorCatalog, source.getSourceId(), "1.2.0", "ConfigHash");

    final Optional<AirbyteCatalog> catalog =
        configRepository.getActorCatalog(source.getSourceId(), "1.2.0", "ConfigHash");
    assertTrue(catalog.isPresent());
    assertEquals(actorCatalog, catalog.get());
    assertFalse(configRepository.getSourceCatalog(source.getSourceId(), "1.3.0", "ConfigHash").isPresent());
    assertFalse(configRepository.getSourceCatalog(source.getSourceId(), "1.2.0", "OtherConfigHash").isPresent());

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.3.0", "ConfigHash");
    final Optional<AirbyteCatalog> catalogNewConnectorVersion =
        configRepository.getActorCatalog(source.getSourceId(), "1.3.0", "ConfigHash");
    assertTrue(catalogNewConnectorVersion.isPresent());
    assertEquals(actorCatalog, catalogNewConnectorVersion.get());

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.2.0", "OtherConfigHash");
    final Optional<AirbyteCatalog> catalogNewConfig =
        configRepository.getActorCatalog(source.getSourceId(), "1.2.0", "OtherConfigHash");
    assertTrue(catalogNewConfig.isPresent());
    assertEquals(actorCatalog, catalogNewConfig.get());

    final int catalogDbEntry = database.query(ctx -> ctx.selectCount().from(ACTOR_CATALOG)).fetchOne().into(int.class);
    assertEquals(1, catalogDbEntry);
  }

  @Test
  public void testListWorkspaceStandardSync() throws IOException {

    final List<StandardSync> syncs = configRepository.listWorkspaceStandardSyncs(MockData.standardWorkspaces().get(0).getWorkspaceId());
    assertThat(MockData.standardSyncs().subList(0, 4)).hasSameElementsAs(syncs);
  }

}
