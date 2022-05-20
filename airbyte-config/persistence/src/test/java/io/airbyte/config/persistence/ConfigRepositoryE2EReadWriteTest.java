/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION_WORKSPACE_GRANT;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION_OPERATION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class ConfigRepositoryE2EReadWriteTest {

  private static PostgreSQLContainer<?> container;
  private DataSource dataSource;
  private DSLContext dslContext;
  private Database database;
  private ConfigRepository configRepository;
  private DatabaseConfigPersistence configPersistence;
  private JsonSecretsProcessor jsonSecretsProcessor;
  private Flyway flyway;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @BeforeEach
  void setup() throws IOException, JsonValidationException, SQLException {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceLoadDataTest.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseInstance(dslContext).getAndInitialize();
    jsonSecretsProcessor = mock(JsonSecretsProcessor.class);
    configPersistence = spy(new DatabaseConfigPersistence(database, jsonSecretsProcessor));
    configRepository = spy(new ConfigRepository(configPersistence, database));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, flyway);
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

    for (final SourceOAuthParameter oAuthParameter : MockData.sourceOauthParameters()) {
      configRepository.writeSourceOAuthParam(oAuthParameter);
    }
    for (final DestinationOAuthParameter oAuthParameter : MockData.destinationOauthParameters()) {
      configRepository.writeDestinationOAuthParam(oAuthParameter);
    }

    database.transaction(ctx -> ctx.truncate(ACTOR_DEFINITION_WORKSPACE_GRANT).execute());
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @Test
  void testWorkspaceCountConnections() throws IOException {

    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    assertEquals(4, configRepository.countConnectionsForWorkspace(workspaceId));
    assertEquals(2, configRepository.countDestinationsForWorkspace(workspaceId));
    assertEquals(2, configRepository.countSourcesForWorkspace(workspaceId));
  }

  @Test
  void testWorkspaceCountConnectionsDeprecated() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(1).getWorkspaceId();
    assertEquals(1, configRepository.countConnectionsForWorkspace(workspaceId));
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

    final Optional<ActorCatalog> catalog =
        configRepository.getActorCatalog(source.getSourceId(), "1.2.0", "ConfigHash");
    assertTrue(catalog.isPresent());
    assertEquals(actorCatalog, Jsons.object(catalog.get().getCatalog(), AirbyteCatalog.class));
    assertFalse(configRepository.getActorCatalog(source.getSourceId(), "1.3.0", "ConfigHash").isPresent());
    assertFalse(configRepository.getActorCatalog(source.getSourceId(), "1.2.0", "OtherConfigHash").isPresent());

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.3.0", "ConfigHash");
    final Optional<ActorCatalog> catalogNewConnectorVersion =
        configRepository.getActorCatalog(source.getSourceId(), "1.3.0", "ConfigHash");
    assertTrue(catalogNewConnectorVersion.isPresent());
    assertEquals(actorCatalog, Jsons.object(catalogNewConnectorVersion.get().getCatalog(), AirbyteCatalog.class));

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.2.0", "OtherConfigHash");
    final Optional<ActorCatalog> catalogNewConfig =
        configRepository.getActorCatalog(source.getSourceId(), "1.2.0", "OtherConfigHash");
    assertTrue(catalogNewConfig.isPresent());
    assertEquals(actorCatalog, Jsons.object(catalogNewConfig.get().getCatalog(), AirbyteCatalog.class));

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
    final StandardSourceDefinition grantableDefinition2 = MockData.grantableSourceDefinition2();
    final StandardSourceDefinition customDefinition = MockData.customSourceDefinition();

    configRepository.writeActorDefinitionWorkspaceGrant(customDefinition.getSourceDefinitionId(), workspaceId);
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition1.getSourceDefinitionId(), workspaceId);
    final List<StandardSourceDefinition> actualGrantedDefinitions = configRepository
        .listGrantedSourceDefinitions(workspaceId, false);
    assertThat(actualGrantedDefinitions).hasSameElementsAs(List.of(grantableDefinition1, customDefinition));

    final List<Entry<StandardSourceDefinition, Boolean>> actualGrantableDefinitions = configRepository
        .listGrantableSourceDefinitions(workspaceId, false);
    assertThat(actualGrantableDefinitions).hasSameElementsAs(List.of(
        Map.entry(grantableDefinition1, true),
        Map.entry(grantableDefinition2, false)));
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
    final StandardDestinationDefinition grantableDefinition2 = MockData.grantableDestinationDefinition2();
    final StandardDestinationDefinition customDefinition = MockData.cusstomDestinationDefinition();

    configRepository.writeActorDefinitionWorkspaceGrant(customDefinition.getDestinationDefinitionId(), workspaceId);
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition1.getDestinationDefinitionId(), workspaceId);
    final List<StandardDestinationDefinition> actualGrantedDefinitions = configRepository
        .listGrantedDestinationDefinitions(workspaceId, false);
    assertThat(actualGrantedDefinitions).hasSameElementsAs(List.of(grantableDefinition1, customDefinition));

    final List<Entry<StandardDestinationDefinition, Boolean>> actualGrantableDefinitions = configRepository
        .listGrantableDestinationDefinitions(workspaceId, false);
    assertThat(actualGrantableDefinitions).hasSameElementsAs(List.of(
        Map.entry(grantableDefinition1, true),
        Map.entry(grantableDefinition2, false)));
  }

  @Test
  public void testWorkspaceCanUseDefinition() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final UUID otherWorkspaceId = MockData.standardWorkspaces().get(1).getWorkspaceId();
    final UUID publicDefinitionId = MockData.publicSourceDefinition().getSourceDefinitionId();
    final UUID grantableDefinition1Id = MockData.grantableSourceDefinition1().getSourceDefinitionId();
    final UUID grantableDefinition2Id = MockData.grantableSourceDefinition2().getSourceDefinitionId();
    final UUID customDefinitionId = MockData.customSourceDefinition().getSourceDefinitionId();

    // Can use public definitions
    assertTrue(configRepository.workspaceCanUseDefinition(publicDefinitionId, workspaceId));

    // Can use granted definitions
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition1Id, workspaceId);
    assertTrue(configRepository.workspaceCanUseDefinition(grantableDefinition1Id, workspaceId));
    configRepository.writeActorDefinitionWorkspaceGrant(customDefinitionId, workspaceId);
    assertTrue(configRepository.workspaceCanUseDefinition(customDefinitionId, workspaceId));

    // Cannot use private definitions without grant
    assertFalse(configRepository.workspaceCanUseDefinition(grantableDefinition2Id, workspaceId));

    // Cannot use other workspace's grants
    configRepository.writeActorDefinitionWorkspaceGrant(grantableDefinition2Id, otherWorkspaceId);
    assertFalse(configRepository.workspaceCanUseDefinition(grantableDefinition2Id, workspaceId));

    // Passing invalid IDs returns false
    assertFalse(configRepository.workspaceCanUseDefinition(new UUID(0L, 0L), workspaceId));

    // workspaceCanUseCustomDefinition can only be true for custom definitions
    assertTrue(configRepository.workspaceCanUseCustomDefinition(customDefinitionId, workspaceId));
    assertFalse(configRepository.workspaceCanUseCustomDefinition(grantableDefinition1Id, workspaceId));
  }

  @Test
  public void testGetDestinationOAuthByDefinitionId() throws IOException {

    final DestinationOAuthParameter destinationOAuthParameter = MockData.destinationOauthParameters().get(0);
    final Optional<DestinationOAuthParameter> result = configRepository.getDestinationOAuthParamByDefinitionIdOptional(
        destinationOAuthParameter.getWorkspaceId(), destinationOAuthParameter.getDestinationDefinitionId());
    assertTrue(result.isPresent());
    assertEquals(destinationOAuthParameter, result.get());
  }

  @Test
  public void testMissingDestinationOAuthByDefinitionId() throws IOException {
    final UUID missingId = UUID.fromString("fc59cfa0-06de-4c8b-850b-46d4cfb65629");
    final DestinationOAuthParameter destinationOAuthParameter = MockData.destinationOauthParameters().get(0);
    Optional<DestinationOAuthParameter> result =
        configRepository.getDestinationOAuthParamByDefinitionIdOptional(destinationOAuthParameter.getWorkspaceId(), missingId);
    assertFalse(result.isPresent());

    result = configRepository.getDestinationOAuthParamByDefinitionIdOptional(missingId, destinationOAuthParameter.getDestinationDefinitionId());
    assertFalse(result.isPresent());
  }

  @Test
  public void testGetSourceOAuthByDefinitionId() throws IOException {
    final SourceOAuthParameter sourceOAuthParameter = MockData.sourceOauthParameters().get(0);
    final Optional<SourceOAuthParameter> result = configRepository.getSourceOAuthParamByDefinitionIdOptional(sourceOAuthParameter.getWorkspaceId(),
        sourceOAuthParameter.getSourceDefinitionId());
    assertTrue(result.isPresent());
    assertEquals(sourceOAuthParameter, result.get());
  }

  @Test
  public void testMissingSourceOAuthByDefinitionId() throws IOException {
    final UUID missingId = UUID.fromString("fc59cfa0-06de-4c8b-850b-46d4cfb65629");
    final SourceOAuthParameter sourceOAuthParameter = MockData.sourceOauthParameters().get(0);
    Optional<SourceOAuthParameter> result =
        configRepository.getSourceOAuthParamByDefinitionIdOptional(sourceOAuthParameter.getWorkspaceId(), missingId);
    assertFalse(result.isPresent());

    result = configRepository.getSourceOAuthParamByDefinitionIdOptional(missingId, sourceOAuthParameter.getSourceDefinitionId());
    assertFalse(result.isPresent());
  }

  @Test
  public void testGetStandardSyncUsingOperation() throws IOException {
    final UUID operationId = MockData.standardSyncOperations().get(0).getOperationId();
    final List<StandardSync> expectedSyncs = MockData.standardSyncs().subList(0, 4);

    final List<StandardSync> syncs = configRepository.listStandardSyncsUsingOperation(operationId);

    assertThat(syncs).hasSameElementsAs(expectedSyncs);

  }

  @Test
  public void testDeleteStandardSyncOperation()
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID deletedOperationId = MockData.standardSyncOperations().get(0).getOperationId();
    final List<StandardSync> syncs = MockData.standardSyncs();
    configRepository.deleteStandardSyncOperation(deletedOperationId);

    for (final StandardSync sync : syncs) {
      final StandardSync retrievedSync = configRepository.getStandardSync(sync.getConnectionId());
      for (final UUID operationId : sync.getOperationIds()) {
        if (operationId.equals(deletedOperationId)) {
          assertThat(retrievedSync.getOperationIds()).doesNotContain(deletedOperationId);
        } else {
          assertThat(retrievedSync.getOperationIds()).contains(operationId);
        }
      }
    }
  }

}
