/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION_OPERATION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
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
  private JsonSecretsProcessor jsonSecretsProcessor;
  private FeatureFlags featureFlags;

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
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    jsonSecretsProcessor = mock(JsonSecretsProcessor.class);
    featureFlags = mock(FeatureFlags.class);
    configPersistence = spy(new DatabaseConfigPersistence(database, jsonSecretsProcessor, featureFlags));
    configRepository = spy(new ConfigRepository(configPersistence, database));
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
    for (final SourceConnection source : MockData.sourceConnections()) {
      configRepository.writeSourceConnectionNoSecrets(source);
    }
    for (final DestinationConnection destination : MockData.destinationConnections()) {
      configRepository.writeDestinationConnectionNoSecrets(destination);
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
    configRepository.writeSourceConnectionNoSecrets(source);

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

  @Test
  public void testGetWorkspaceBySlug()
      throws IOException {

    final StandardWorkspace workspace = MockData.standardWorkspaces().get(0);
    final StandardWorkspace tombstonedWorkspace = MockData.standardWorkspaces().get(2);
    final Optional<StandardWorkspace> retrievedWorkspace = configRepository.getWorkspaceBySlugOptional(workspace.getSlug(), false);
    final Optional<StandardWorkspace> retrievedTombstonedWorkspaceNoTombstone =
        configRepository.getWorkspaceBySlugOptional(tombstonedWorkspace.getSlug(), false);
    final Optional<StandardWorkspace> retrievedTombstonedWorkspace = configRepository.getWorkspaceBySlugOptional(tombstonedWorkspace.getSlug(), true);

    assertTrue(retrievedWorkspace.isPresent());
    assertEquals(workspace, retrievedWorkspace.get());

    assertFalse(retrievedTombstonedWorkspaceNoTombstone.isPresent());
    assertTrue(retrievedTombstonedWorkspace.isPresent());

    assertEquals(tombstonedWorkspace, retrievedTombstonedWorkspace.get());
  }

  @Test
  public void testUpdateConnectionOperationIds() throws Exception {
    final StandardSync sync = MockData.standardSyncs().get(0);
    final List<UUID> existingOperationIds = sync.getOperationIds();
    final UUID connectionId = sync.getConnectionId();

    // this test only works as intended when there are multiple operationIds
    assertTrue(existingOperationIds.size() > 1);

    // first, remove all associated operations
    Set<UUID> expectedOperationIds = Collections.emptySet();
    configRepository.updateConnectionOperationIds(connectionId, expectedOperationIds);
    Set<UUID> actualOperationIds = fetchOperationIdsForConnectionId(connectionId);
    assertEquals(expectedOperationIds, actualOperationIds);

    // now, add back one operation
    expectedOperationIds = Collections.singleton(existingOperationIds.get(0));
    configRepository.updateConnectionOperationIds(connectionId, expectedOperationIds);
    actualOperationIds = fetchOperationIdsForConnectionId(connectionId);
    assertEquals(expectedOperationIds, actualOperationIds);

    // finally, remove the first operation while adding back in the rest
    expectedOperationIds = existingOperationIds.stream().skip(1).collect(Collectors.toSet());
    configRepository.updateConnectionOperationIds(connectionId, expectedOperationIds);
    actualOperationIds = fetchOperationIdsForConnectionId(connectionId);
    assertEquals(expectedOperationIds, actualOperationIds);
  }

  private Set<UUID> fetchOperationIdsForConnectionId(final UUID connectionId) throws SQLException {
    return database.query(ctx -> ctx
        .selectFrom(CONNECTION_OPERATION)
        .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
        .fetchSet(CONNECTION_OPERATION.OPERATION_ID));
  }

  @Test
  public void testActorDefinitionWorkspaceGrantExists() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final UUID definitionId = MockData.standardSourceDefinitions().get(0).getSourceDefinitionId();

    assertFalse(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));

    configRepository.writeActorDefinitionWorkspaceGrant(definitionId, workspaceId);
    assertTrue(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));

    configRepository.deleteActorDefinitionWorkspaceGrant(definitionId, workspaceId);
    assertFalse(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));
  }

  @Test
  public void testListPublicSourceDefinitions() throws IOException {
    final List<StandardSourceDefinition> actualDefinitions = configRepository.listPublicSourceDefinitions(false);
    assertEquals(List.of(MockData.publicSourceDefinition()), actualDefinitions);
  }

  @Test
  public void testSourceDefinitionGrants() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final StandardSourceDefinition grantableDefinition1 = MockData.grantableSourceDefinition1();
    final StandardSourceDefinition customDefinition = MockData.customSourceDefinition();

    configRepository.writeActorDefinitionWorkspaceGrant(customDefinition.getSourceDefinitionId(), workspaceId);
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition1.getSourceDefinitionId(), workspaceId);
    final List<StandardSourceDefinition> actualGrantedDefinitions = configRepository
        .listGrantedSourceDefinitions(workspaceId, false);
    assertThat(actualGrantedDefinitions).hasSameElementsAs(List.of(grantableDefinition1, customDefinition));
  }

  @Test
  public void testListPublicDestinationDefinitions() throws IOException {
    final List<StandardDestinationDefinition> actualDefinitions = configRepository.listPublicDestinationDefinitions(false);
    assertEquals(List.of(MockData.publicDestinationDefinition()), actualDefinitions);
  }

  @Test
  public void testDestinationDefinitionGrants() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final StandardDestinationDefinition grantableDefinition1 = MockData.grantableDestinationDefinition1();
    final StandardDestinationDefinition customDefinition = MockData.cusstomDestinationDefinition();

    configRepository.writeActorDefinitionWorkspaceGrant(customDefinition.getDestinationDefinitionId(), workspaceId);
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition1.getDestinationDefinitionId(), workspaceId);
    final List<StandardDestinationDefinition> actualGrantedDefinitions = configRepository
        .listGrantedDestinationDefinitions(workspaceId, false);
    assertThat(actualGrantedDefinitions).hasSameElementsAs(List.of(grantableDefinition1, customDefinition));
  }

}
