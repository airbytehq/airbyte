/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION_WORKSPACE_GRANT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION_OPERATION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.jooq.impl.DSL.select;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.Geography;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository.DestinationAndDefinition;
import io.airbyte.config.persistence.ConfigRepository.SourceAndDefinition;
import io.airbyte.config.persistence.ConfigRepository.StandardSyncQuery;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * The tests in this class should be moved into separate test suites grouped by resource. Do NOT add
 * new tests here. Add them to resource based test suites (e.g. WorkspacePersistenceTest). If one
 * does not exist yet for that resource yet, create one and follow the pattern.
 */
@Deprecated
@SuppressWarnings({"PMD.CyclomaticComplexity", "PMD.NPathComplexity"})
class ConfigRepositoryE2EReadWriteTest extends BaseConfigDatabaseTest {

  private final static String DOCKER_IMAGE_TAG = "1.2.0";
  private final static String CONFIG_HASH = "ConfigHash";

  private ConfigRepository configRepository;

  @BeforeEach
  void setup() throws IOException, JsonValidationException, SQLException {
    configRepository = spy(new ConfigRepository(
        database,
        new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database)),
        new StandardSyncPersistence(database)));
    for (final StandardWorkspace workspace : MockData.standardWorkspaces()) {
      configRepository.writeStandardWorkspaceNoSecrets(workspace);
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

  @Test
  void testWorkspaceCountConnections() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    assertEquals(3, configRepository.countConnectionsForWorkspace(workspaceId));
    assertEquals(2, configRepository.countDestinationsForWorkspace(workspaceId));
    assertEquals(2, configRepository.countSourcesForWorkspace(workspaceId));
  }

  @Test
  void testWorkspaceCountConnectionsDeprecated() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(1).getWorkspaceId();
    assertEquals(1, configRepository.countConnectionsForWorkspace(workspaceId));
  }

  @Test
  void testFetchActorsUsingDefinition() throws IOException {
    final UUID destinationDefinitionId = MockData.publicDestinationDefinition().getDestinationDefinitionId();
    final UUID sourceDefinitionId = MockData.publicSourceDefinition().getSourceDefinitionId();
    final List<DestinationConnection> destinationConnections = configRepository.listDestinationsForDefinition(
        destinationDefinitionId);
    final List<SourceConnection> sourceConnections = configRepository.listSourcesForDefinition(
        sourceDefinitionId);

    assertThat(destinationConnections)
        .containsExactlyElementsOf(MockData.destinationConnections().stream().filter(d -> d.getDestinationDefinitionId().equals(
            destinationDefinitionId) && !d.getTombstone()).collect(Collectors.toList()));
    assertThat(sourceConnections).containsExactlyElementsOf(MockData.sourceConnections().stream().filter(d -> d.getSourceDefinitionId().equals(
        sourceDefinitionId) && !d.getTombstone()).collect(Collectors.toList()));
  }

  @Test
  void testSimpleInsertActorCatalog() throws IOException, JsonValidationException, SQLException {
    final String otherConfigHash = "OtherConfigHash";
    final StandardWorkspace workspace = MockData.standardWorkspaces().get(0);

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withSourceType(SourceType.DATABASE)
        .withDockerRepository("docker-repo")
        .withDockerImageTag(DOCKER_IMAGE_TAG)
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
    final AirbyteCatalog expectedActorCatalog = CatalogHelpers.createAirbyteCatalog("clothes", Field.of("name", JsonSchemaType.STRING_V1));
    configRepository.writeActorCatalogFetchEvent(
        actorCatalog, source.getSourceId(), DOCKER_IMAGE_TAG, CONFIG_HASH);

    final Optional<ActorCatalog> catalog =
        configRepository.getActorCatalog(source.getSourceId(), DOCKER_IMAGE_TAG, CONFIG_HASH);
    assertTrue(catalog.isPresent());
    assertEquals(expectedActorCatalog, Jsons.object(catalog.get().getCatalog(), AirbyteCatalog.class));
    assertFalse(configRepository.getActorCatalog(source.getSourceId(), "1.3.0", CONFIG_HASH).isPresent());
    assertFalse(configRepository.getActorCatalog(source.getSourceId(), DOCKER_IMAGE_TAG, otherConfigHash).isPresent());

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.3.0", CONFIG_HASH);
    final Optional<ActorCatalog> catalogNewConnectorVersion =
        configRepository.getActorCatalog(source.getSourceId(), "1.3.0", CONFIG_HASH);
    assertTrue(catalogNewConnectorVersion.isPresent());
    assertEquals(expectedActorCatalog, Jsons.object(catalogNewConnectorVersion.get().getCatalog(), AirbyteCatalog.class));

    configRepository.writeActorCatalogFetchEvent(actorCatalog, source.getSourceId(), "1.2.0", otherConfigHash);
    final Optional<ActorCatalog> catalogNewConfig =
        configRepository.getActorCatalog(source.getSourceId(), DOCKER_IMAGE_TAG, otherConfigHash);
    assertTrue(catalogNewConfig.isPresent());
    assertEquals(expectedActorCatalog, Jsons.object(catalogNewConfig.get().getCatalog(), AirbyteCatalog.class));

    final int catalogDbEntry = database.query(ctx -> ctx.selectCount().from(ACTOR_CATALOG)).fetchOne().into(int.class);
    assertEquals(1, catalogDbEntry);

    // Writing the previous catalog with v1 data types
    configRepository.writeActorCatalogFetchEvent(expectedActorCatalog, source.getSourceId(), "1.2.0", otherConfigHash);
    final Optional<ActorCatalog> catalogV1NewConfig =
        configRepository.getActorCatalog(source.getSourceId(), DOCKER_IMAGE_TAG, otherConfigHash);
    assertTrue(catalogV1NewConfig.isPresent());
    assertEquals(expectedActorCatalog, Jsons.object(catalogNewConfig.get().getCatalog(), AirbyteCatalog.class));

    configRepository.writeActorCatalogFetchEvent(expectedActorCatalog, source.getSourceId(), "1.4.0", otherConfigHash);
    final Optional<ActorCatalog> catalogV1again =
        configRepository.getActorCatalog(source.getSourceId(), DOCKER_IMAGE_TAG, otherConfigHash);
    assertTrue(catalogV1again.isPresent());
    assertEquals(expectedActorCatalog, Jsons.object(catalogNewConfig.get().getCatalog(), AirbyteCatalog.class));

    final int catalogDbEntry2 = database.query(ctx -> ctx.selectCount().from(ACTOR_CATALOG)).fetchOne().into(int.class);
    assertEquals(2, catalogDbEntry2);
  }

  @Test
  void testListWorkspaceStandardSyncAll() throws IOException {
    final List<StandardSync> expectedSyncs = copyWithV1Types(MockData.standardSyncs().subList(0, 4));
    final List<StandardSync> actualSyncs = configRepository.listWorkspaceStandardSyncs(
        MockData.standardWorkspaces().get(0).getWorkspaceId(), true);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  @Test
  void testListWorkspaceStandardSyncWithAllFiltering() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final StandardSyncQuery query = new StandardSyncQuery(workspaceId, List.of(MockData.SOURCE_ID_1), List.of(MockData.DESTINATION_ID_1), false);
    final List<StandardSync> expectedSyncs = copyWithV1Types(
        MockData.standardSyncs().subList(0, 3).stream()
            .filter(sync -> query.destinationId().contains(sync.getDestinationId()))
            .filter(sync -> query.sourceId().contains(sync.getSourceId()))
            .toList());
    final List<StandardSync> actualSyncs = configRepository.listWorkspaceStandardSyncs(query);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  @Test
  void testListWorkspaceStandardSyncDestinationFiltering() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final StandardSyncQuery query = new StandardSyncQuery(workspaceId, null, List.of(MockData.DESTINATION_ID_1), false);
    final List<StandardSync> expectedSyncs = copyWithV1Types(
        MockData.standardSyncs().subList(0, 3).stream()
            .filter(sync -> query.destinationId().contains(sync.getDestinationId()))
            .toList());
    final List<StandardSync> actualSyncs = configRepository.listWorkspaceStandardSyncs(query);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  @Test
  void testListWorkspaceStandardSyncSourceFiltering() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final StandardSyncQuery query = new StandardSyncQuery(workspaceId, List.of(MockData.SOURCE_ID_2), null, false);
    final List<StandardSync> expectedSyncs = copyWithV1Types(
        MockData.standardSyncs().subList(0, 3).stream()
            .filter(sync -> query.sourceId().contains(sync.getSourceId()))
            .toList());
    final List<StandardSync> actualSyncs = configRepository.listWorkspaceStandardSyncs(query);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  @Test
  void testListWorkspaceStandardSyncExcludeDeleted() throws IOException {
    final List<StandardSync> expectedSyncs = copyWithV1Types(MockData.standardSyncs().subList(0, 3));
    final List<StandardSync> actualSyncs = configRepository.listWorkspaceStandardSyncs(MockData.standardWorkspaces().get(0).getWorkspaceId(), false);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  @Test
  void testGetWorkspaceBySlug() throws IOException {
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
  void testUpdateConnectionOperationIds() throws Exception {
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
  void testActorDefinitionWorkspaceGrantExists() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final UUID definitionId = MockData.standardSourceDefinitions().get(0).getSourceDefinitionId();

    assertFalse(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));

    configRepository.writeActorDefinitionWorkspaceGrant(definitionId, workspaceId);
    assertTrue(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));

    configRepository.deleteActorDefinitionWorkspaceGrant(definitionId, workspaceId);
    assertFalse(configRepository.actorDefinitionWorkspaceGrantExists(definitionId, workspaceId));
  }

  @Test
  void testListPublicSourceDefinitions() throws IOException {
    final List<StandardSourceDefinition> actualDefinitions = configRepository.listPublicSourceDefinitions(false);
    assertEquals(List.of(MockData.publicSourceDefinition()), actualDefinitions);
  }

  @Test
  void testListWorkspaceSources() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(1).getWorkspaceId();
    final List<SourceConnection> expectedSources = MockData.sourceConnections().stream()
        .filter(source -> source.getWorkspaceId().equals(workspaceId)).collect(Collectors.toList());
    final List<SourceConnection> sources = configRepository.listWorkspaceSourceConnection(workspaceId);
    assertThat(sources).hasSameElementsAs(expectedSources);
  }

  @Test
  void testListWorkspaceDestinations() throws IOException {
    final UUID workspaceId = MockData.standardWorkspaces().get(0).getWorkspaceId();
    final List<DestinationConnection> expectedDestinations = MockData.destinationConnections().stream()
        .filter(destination -> destination.getWorkspaceId().equals(workspaceId)).collect(Collectors.toList());
    final List<DestinationConnection> destinations = configRepository.listWorkspaceDestinationConnection(workspaceId);
    assertThat(destinations).hasSameElementsAs(expectedDestinations);
  }

  @Test
  void testSourceDefinitionGrants() throws IOException {
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
  void testListPublicDestinationDefinitions() throws IOException {
    final List<StandardDestinationDefinition> actualDefinitions = configRepository.listPublicDestinationDefinitions(false);
    assertEquals(List.of(MockData.publicDestinationDefinition()), actualDefinitions);
  }

  @Test
  void testDestinationDefinitionGrants() throws IOException {
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
  void testWorkspaceCanUseDefinition() throws IOException {
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
  void testGetDestinationOAuthByDefinitionId() throws IOException {

    final DestinationOAuthParameter destinationOAuthParameter = MockData.destinationOauthParameters().get(0);
    final Optional<DestinationOAuthParameter> result = configRepository.getDestinationOAuthParamByDefinitionIdOptional(
        destinationOAuthParameter.getWorkspaceId(), destinationOAuthParameter.getDestinationDefinitionId());
    assertTrue(result.isPresent());
    assertEquals(destinationOAuthParameter, result.get());
  }

  @Test
  void testMissingDestinationOAuthByDefinitionId() throws IOException {
    final UUID missingId = UUID.fromString("fc59cfa0-06de-4c8b-850b-46d4cfb65629");
    final DestinationOAuthParameter destinationOAuthParameter = MockData.destinationOauthParameters().get(0);
    Optional<DestinationOAuthParameter> result =
        configRepository.getDestinationOAuthParamByDefinitionIdOptional(destinationOAuthParameter.getWorkspaceId(), missingId);
    assertFalse(result.isPresent());

    result = configRepository.getDestinationOAuthParamByDefinitionIdOptional(missingId, destinationOAuthParameter.getDestinationDefinitionId());
    assertFalse(result.isPresent());
  }

  @Test
  void testGetSourceOAuthByDefinitionId() throws IOException {
    final SourceOAuthParameter sourceOAuthParameter = MockData.sourceOauthParameters().get(0);
    final Optional<SourceOAuthParameter> result = configRepository.getSourceOAuthParamByDefinitionIdOptional(sourceOAuthParameter.getWorkspaceId(),
        sourceOAuthParameter.getSourceDefinitionId());
    assertTrue(result.isPresent());
    assertEquals(sourceOAuthParameter, result.get());
  }

  @Test
  void testMissingSourceOAuthByDefinitionId() throws IOException {
    final UUID missingId = UUID.fromString("fc59cfa0-06de-4c8b-850b-46d4cfb65629");
    final SourceOAuthParameter sourceOAuthParameter = MockData.sourceOauthParameters().get(0);
    Optional<SourceOAuthParameter> result =
        configRepository.getSourceOAuthParamByDefinitionIdOptional(sourceOAuthParameter.getWorkspaceId(), missingId);
    assertFalse(result.isPresent());

    result = configRepository.getSourceOAuthParamByDefinitionIdOptional(missingId, sourceOAuthParameter.getSourceDefinitionId());
    assertFalse(result.isPresent());
  }

  @Test
  void testGetStandardSyncUsingOperation() throws IOException {
    final UUID operationId = MockData.standardSyncOperations().get(0).getOperationId();
    final List<StandardSync> expectedSyncs = copyWithV1Types(MockData.standardSyncs().subList(0, 3));
    final List<StandardSync> actualSyncs = configRepository.listStandardSyncsUsingOperation(operationId);

    assertSyncsMatch(expectedSyncs, actualSyncs);
  }

  private List<StandardSync> copyWithV1Types(final List<StandardSync> syncs) {
    return syncs.stream()
        .map(standardSync -> {
          final StandardSync copiedStandardSync = Jsons.deserialize(Jsons.serialize(standardSync), StandardSync.class);
          copiedStandardSync.setCatalog(MockData.getConfiguredCatalogWithV1DataTypes());
          return copiedStandardSync;
        })
        .toList();
  }

  private void assertSyncsMatch(final List<StandardSync> expectedSyncs, final List<StandardSync> actualSyncs) {
    assertEquals(expectedSyncs.size(), actualSyncs.size());

    for (final StandardSync expected : expectedSyncs) {

      final Optional<StandardSync> maybeActual = actualSyncs.stream().filter(s -> s.getConnectionId().equals(expected.getConnectionId())).findFirst();
      if (maybeActual.isEmpty()) {
        Assertions.fail(String.format("Expected to find connectionId %s in result, but actual connectionIds are %s",
            expected.getConnectionId(),
            actualSyncs.stream().map(StandardSync::getConnectionId).collect(Collectors.toList())));
      }
      final StandardSync actual = maybeActual.get();

      // operationIds can be ordered differently in the query result than in the mock data, so they need
      // to be verified separately
      // from the rest of the sync.
      assertThat(actual.getOperationIds()).hasSameElementsAs(expected.getOperationIds());

      // now, clear operationIds so the rest of the sync can be compared
      expected.setOperationIds(null);
      actual.setOperationIds(null);
      assertEquals(expected, actual);
    }
  }

  @Test
  void testDeleteStandardSyncOperation()
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

  @Test
  void testGetSourceAndDefinitionsFromSourceIds() throws IOException {
    final List<UUID> sourceIds = MockData.sourceConnections().subList(0, 2).stream().map(SourceConnection::getSourceId).toList();

    final List<SourceAndDefinition> expected = List.of(
        new SourceAndDefinition(MockData.sourceConnections().get(0), MockData.standardSourceDefinitions().get(0)),
        new SourceAndDefinition(MockData.sourceConnections().get(1), MockData.standardSourceDefinitions().get(1)));

    final List<SourceAndDefinition> actual = configRepository.getSourceAndDefinitionsFromSourceIds(sourceIds);
    assertThat(actual).hasSameElementsAs(expected);
  }

  @Test
  void testGetDestinationAndDefinitionsFromDestinationIds() throws IOException {
    final List<UUID> destinationIds = MockData.destinationConnections().subList(0, 2).stream().map(DestinationConnection::getDestinationId).toList();

    final List<DestinationAndDefinition> expected = List.of(
        new DestinationAndDefinition(MockData.destinationConnections().get(0), MockData.standardDestinationDefinitions().get(0)),
        new DestinationAndDefinition(MockData.destinationConnections().get(1), MockData.standardDestinationDefinitions().get(1)));

    final List<DestinationAndDefinition> actual = configRepository.getDestinationAndDefinitionsFromDestinationIds(destinationIds);
    assertThat(actual).hasSameElementsAs(expected);
  }

  @Test
  void testGetGeographyForConnection() throws IOException {
    final StandardSync sync = MockData.standardSyncs().get(0);
    final Geography expected = sync.getGeography();
    final Geography actual = configRepository.getGeographyForConnection(sync.getConnectionId());

    assertEquals(expected, actual);
  }

  @SuppressWarnings("OptionalGetWithoutIsPresent")
  @Test
  void testGetMostRecentActorCatalogFetchEventForSource() throws SQLException, IOException {
    for (final ActorCatalog actorCatalog : MockData.actorCatalogs()) {
      writeActorCatalog(database, Collections.singletonList(actorCatalog));
    }

    final OffsetDateTime now = OffsetDateTime.now();
    final OffsetDateTime yesterday = now.minusDays(1L);

    final List<ActorCatalogFetchEvent> fetchEvents = MockData.actorCatalogFetchEventsSameSource();
    final ActorCatalogFetchEvent fetchEvent1 = fetchEvents.get(0);
    final ActorCatalogFetchEvent fetchEvent2 = fetchEvents.get(1);

    database.transaction(ctx -> {
      insertCatalogFetchEvent(
          ctx,
          fetchEvent1.getActorId(),
          fetchEvent1.getActorCatalogId(),
          yesterday);
      insertCatalogFetchEvent(
          ctx,
          fetchEvent2.getActorId(),
          fetchEvent2.getActorCatalogId(),
          now);
      // Insert a second identical copy to verify that the query can handle duplicates since the records
      // are not guaranteed to be unique.
      insertCatalogFetchEvent(
          ctx,
          fetchEvent2.getActorId(),
          fetchEvent2.getActorCatalogId(),
          now);

      return null;
    });

    final Optional<ActorCatalogFetchEvent> result =
        configRepository.getMostRecentActorCatalogFetchEventForSource(fetchEvent1.getActorId());

    assertEquals(fetchEvent2.getActorCatalogId(), result.get().getActorCatalogId());
  }

  @Test
  void testGetMostRecentActorCatalogFetchEventForSources() throws SQLException, IOException {
    for (final ActorCatalog actorCatalog : MockData.actorCatalogs()) {
      writeActorCatalog(database, Collections.singletonList(actorCatalog));
    }

    database.transaction(ctx -> {
      MockData.actorCatalogFetchEventsForAggregationTest().forEach(actorCatalogFetchEvent -> insertCatalogFetchEvent(
          ctx,
          actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorId(),
          actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorCatalogId(),
          actorCatalogFetchEvent.getCreatedAt()));

      return null;
    });

    final Map<UUID, ActorCatalogFetchEvent> result =
        configRepository.getMostRecentActorCatalogFetchEventForSources(List.of(MockData.SOURCE_ID_1,
            MockData.SOURCE_ID_2));

    assertEquals(MockData.ACTOR_CATALOG_ID_1, result.get(MockData.SOURCE_ID_1).getActorCatalogId());
    assertEquals(MockData.ACTOR_CATALOG_ID_3, result.get(MockData.SOURCE_ID_2).getActorCatalogId());
    assertEquals(0, configRepository.getMostRecentActorCatalogFetchEventForSources(Collections.emptyList()).size());
  }

  @Test
  void testGetMostRecentActorCatalogFetchEventWithDuplicates() throws SQLException, IOException {
    // Tests that we can handle two fetch events in the db with the same actor id, actor catalog id, and
    // timestamp e.g., from duplicate discoveries.
    for (final ActorCatalog actorCatalog : MockData.actorCatalogs()) {
      writeActorCatalog(database, Collections.singletonList(actorCatalog));
    }

    database.transaction(ctx -> {
      // Insert the fetch events twice.
      MockData.actorCatalogFetchEventsForAggregationTest().forEach(actorCatalogFetchEvent -> {
        insertCatalogFetchEvent(
            ctx,
            actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorId(),
            actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorCatalogId(),
            actorCatalogFetchEvent.getCreatedAt());
        insertCatalogFetchEvent(
            ctx,
            actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorId(),
            actorCatalogFetchEvent.getActorCatalogFetchEvent().getActorCatalogId(),
            actorCatalogFetchEvent.getCreatedAt());
      });
      return null;
    });

    final Map<UUID, ActorCatalogFetchEvent> result =
        configRepository.getMostRecentActorCatalogFetchEventForSources(List.of(MockData.SOURCE_ID_1,
            MockData.SOURCE_ID_2));

    assertEquals(MockData.ACTOR_CATALOG_ID_1, result.get(MockData.SOURCE_ID_1).getActorCatalogId());
    assertEquals(MockData.ACTOR_CATALOG_ID_3, result.get(MockData.SOURCE_ID_2).getActorCatalogId());
  }

  @Test
  void testGetActorDefinitionsInUseToProtocolVersion() throws IOException {
    final Set<UUID> actorDefinitionIds = new HashSet<>();
    actorDefinitionIds.addAll(MockData.sourceConnections().stream().map(SourceConnection::getSourceDefinitionId).toList());
    actorDefinitionIds.addAll(MockData.destinationConnections().stream().map(DestinationConnection::getDestinationDefinitionId).toList());
    assertEquals(actorDefinitionIds, configRepository.getActorDefinitionToProtocolVersionMap().keySet());
  }

  private void insertCatalogFetchEvent(final DSLContext ctx, final UUID sourceId, final UUID catalogId, final OffsetDateTime creationDate) {
    ctx.insertInto(ACTOR_CATALOG_FETCH_EVENT)
        .columns(
            ACTOR_CATALOG_FETCH_EVENT.ID,
            ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID,
            ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID,
            ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH,
            ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION,
            ACTOR_CATALOG_FETCH_EVENT.CREATED_AT,
            ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT)
        .values(UUID.randomUUID(), sourceId, catalogId, "", "", creationDate, creationDate)
        .execute();
  }

  private static void writeActorCatalog(final Database database, final List<ActorCatalog> configs) throws SQLException {
    database.transaction(ctx -> {
      writeActorCatalog(configs, ctx);
      return null;
    });
  }

  private static void writeActorCatalog(final List<ActorCatalog> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((actorCatalog) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_CATALOG)
          .where(ACTOR_CATALOG.ID.eq(actorCatalog.getId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_CATALOG)
            .set(ACTOR_CATALOG.CATALOG, JSONB.valueOf(Jsons.serialize(actorCatalog.getCatalog())))
            .set(ACTOR_CATALOG.CATALOG_HASH, actorCatalog.getCatalogHash())
            .set(ACTOR_CATALOG.MODIFIED_AT, timestamp)
            .where(ACTOR_CATALOG.ID.eq(actorCatalog.getId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR_CATALOG)
            .set(ACTOR_CATALOG.ID, actorCatalog.getId())
            .set(ACTOR_CATALOG.CATALOG, JSONB.valueOf(Jsons.serialize(actorCatalog.getCatalog())))
            .set(ACTOR_CATALOG.CATALOG_HASH, actorCatalog.getCatalogHash())
            .set(ACTOR_CATALOG.CREATED_AT, timestamp)
            .set(ACTOR_CATALOG.MODIFIED_AT, timestamp)
            .execute();
      }
    });
  }

}
