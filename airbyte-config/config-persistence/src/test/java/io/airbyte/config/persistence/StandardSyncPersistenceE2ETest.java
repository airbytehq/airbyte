/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.ActorType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Geography;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StandardSyncPersistenceE2ETest extends BaseDatabaseConfigPersistenceTest {

  record StandardSyncProtocolVersionFlag(UUID standardSyncId, boolean unsupportedProtocolVersion) {}

  private ConfigRepository configRepository;

  UUID workspaceId;
  StandardWorkspace workspace;
  StandardSourceDefinition sourceDef1;
  StandardSourceDefinition sourceDef2;
  SourceConnection source1;
  SourceConnection source2;
  StandardDestinationDefinition destDef1;
  StandardDestinationDefinition destDef2;
  DestinationConnection destination1;
  DestinationConnection destination2;

  final AirbyteProtocolVersionRange protocolRange_0_0 = new AirbyteProtocolVersionRange(new Version("0.0.0"), new Version("0.1.0"));
  final AirbyteProtocolVersionRange protocolRange_0_1 = new AirbyteProtocolVersionRange(new Version("0.0.1"), new Version("1.0.0"));
  final AirbyteProtocolVersionRange protocolRange_1_1 = new AirbyteProtocolVersionRange(new Version("1.0.0"), new Version("1.10.0"));

  @BeforeEach
  void beforeEach() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    flyway = FlywayFactory.create(dataSource, StandardSyncPersistenceE2ETest.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseTestProvider(dslContext, flyway).create(true);
    truncateAllTables();

    standardSyncPersistence = new StandardSyncPersistence(database);
    configRepository = new ConfigRepository(database);
  }

  @AfterEach
  void afterEach() throws Exception {
    dslContext.close();
    DataSourceFactory.close(dataSource);
  }

  @Test
  void testClearUnsupportedProtocolVersionFlagFromSource() throws IOException, JsonValidationException, SQLException {
    createBaseObjects();

    final StandardSync sync1 = createStandardSync(source1, destination1);
    final StandardSync sync2 = createStandardSync(source1, destination2);
    final List<StandardSync> syncs = List.of(sync1, sync2);

    setProtocolVersionFlagForSyncs(List.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), true),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), true)));

    // Only sync1 should be flipped since sync2 has dest2 with protocol v1
    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(sourceDef1.getSourceDefinitionId(), ActorType.SOURCE, protocolRange_0_0);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), false),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), true)), getProtocolVersionFlagForSyncs(syncs));

    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(sourceDef1.getSourceDefinitionId(), ActorType.SOURCE, protocolRange_0_1);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), false),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), false)), getProtocolVersionFlagForSyncs(syncs));

    // Making sure we updated the updated_at timestamp
    final Optional<Pair<OffsetDateTime, OffsetDateTime>> datetimes = database.query(ctx -> ctx
        .select(CONNECTION.CREATED_AT, CONNECTION.UPDATED_AT).from(CONNECTION).where(CONNECTION.ID.eq(sync2.getConnectionId()))
        .stream().findFirst()
        .map(r -> new ImmutablePair<>(r.get(CONNECTION.CREATED_AT), r.get(CONNECTION.UPDATED_AT))));
    assertTrue(datetimes.isPresent());
    assertNotEquals(datetimes.get().getLeft(), datetimes.get().getRight());
  }

  @Test
  void testClearUnsupportedProtocolVersionFlagFromSourceMultiFlipAtOnce() throws IOException, JsonValidationException, SQLException {
    createBaseObjects();

    final StandardSync sync1 = createStandardSync(source1, destination1);
    final StandardSync sync2 = createStandardSync(source1, destination2);
    final List<StandardSync> syncs = List.of(sync1, sync2);

    setProtocolVersionFlagForSyncs(List.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), true),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), true)));

    // Making sure we flip all the connections if more than one is impacted
    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(sourceDef1.getSourceDefinitionId(), ActorType.SOURCE, protocolRange_0_1);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), false),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), false)), getProtocolVersionFlagForSyncs(syncs));
  }

  @Test
  void testClearUnsupportedProtocolVersionFlagFromDest() throws IOException, JsonValidationException, SQLException {
    createBaseObjects();

    final StandardSync sync1 = createStandardSync(source1, destination2);
    final StandardSync sync2 = createStandardSync(source2, destination2);
    final List<StandardSync> syncs = List.of(sync1, sync2);

    setProtocolVersionFlagForSyncs(List.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), true),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), true)));

    // destDef1 is not tied to anything, there should be no change
    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(destDef1.getDestinationDefinitionId(), ActorType.DESTINATION, protocolRange_0_1);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), true),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), true)), getProtocolVersionFlagForSyncs(syncs));

    // Only sync1 should be flipped since sync2 has source1 with protocol v0
    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(destDef2.getDestinationDefinitionId(), ActorType.DESTINATION, protocolRange_1_1);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), true),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), false)), getProtocolVersionFlagForSyncs(syncs));

    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(destDef2.getDestinationDefinitionId(), ActorType.DESTINATION, protocolRange_0_1);
    assertEquals(Set.of(
        new StandardSyncProtocolVersionFlag(sync1.getConnectionId(), false),
        new StandardSyncProtocolVersionFlag(sync2.getConnectionId(), false)), getProtocolVersionFlagForSyncs(syncs));
  }

  Set<StandardSyncProtocolVersionFlag> getProtocolVersionFlagForSyncs(final List<StandardSync> standardSync) throws SQLException {
    return database.query(ctx -> ctx
        .select(CONNECTION.ID, CONNECTION.UNSUPPORTED_PROTOCOL_VERSION)
        .from(CONNECTION)
        .where(CONNECTION.ID.in(standardSync.stream().map(StandardSync::getConnectionId).toList()))
        .fetchStream())
        .map(r -> new StandardSyncProtocolVersionFlag(r.get(CONNECTION.ID), r.get(CONNECTION.UNSUPPORTED_PROTOCOL_VERSION)))
        .collect(Collectors.toSet());
  }

  void setProtocolVersionFlagForSyncs(final List<StandardSyncProtocolVersionFlag> updates) throws SQLException {
    final List<UUID> setToTrue =
        updates.stream().filter(s -> s.unsupportedProtocolVersion).map(StandardSyncProtocolVersionFlag::standardSyncId).toList();
    final List<UUID> setToFalse =
        updates.stream().filter(s -> !s.unsupportedProtocolVersion).map(StandardSyncProtocolVersionFlag::standardSyncId).toList();
    database.query(ctx -> {
      if (!setToTrue.isEmpty()) {
        ctx.update(CONNECTION)
            .set(CONNECTION.UNSUPPORTED_PROTOCOL_VERSION, true)
            .where(CONNECTION.ID.in(setToTrue))
            .execute();
      }
      if (!setToFalse.isEmpty()) {
        ctx.update(CONNECTION)
            .set(CONNECTION.UNSUPPORTED_PROTOCOL_VERSION, false)
            .where(CONNECTION.ID.in(setToFalse))
            .execute();
      }
      return null;
    });
  }

  private void createBaseObjects() throws IOException, JsonValidationException {
    workspaceId = UUID.randomUUID();
    workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName("Another Workspace")
        .withSlug("another-workspace")
        .withInitialSetupComplete(true)
        .withTombstone(false)
        .withDefaultGeography(Geography.AUTO);
    configRepository.writeStandardWorkspaceNoSecrets(workspace);

    sourceDef1 = createStandardSourceDefinition("0.2.2");
    source1 = createSourceConnection(workspaceId, sourceDef1);

    sourceDef2 = createStandardSourceDefinition("1.1.0");
    source2 = createSourceConnection(workspaceId, sourceDef2);

    destDef1 = createStandardDestDefinition("0.2.3");
    destination1 = createDestinationConnection(workspaceId, destDef1);

    destDef2 = createStandardDestDefinition("1.0.0");
    destination2 = createDestinationConnection(workspaceId, destDef2);
  }

  private StandardSourceDefinition createStandardSourceDefinition(final String protocolVersion) throws JsonValidationException, IOException {
    final UUID sourceDefId = UUID.randomUUID();
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition()
        .withSourceDefinitionId(sourceDefId)
        .withSourceType(SourceType.API)
        .withName("random-source-" + sourceDefId)
        .withDockerImageTag("tag-1")
        .withDockerRepository("repository-1")
        .withDocumentationUrl("documentation-url-1")
        .withIcon("icon-1")
        .withSpec(new ConnectorSpecification())
        .withProtocolVersion(protocolVersion)
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
    configRepository.writeStandardSourceDefinition(sourceDef);
    return sourceDef;
  }

  private StandardDestinationDefinition createStandardDestDefinition(final String protocolVersion) throws JsonValidationException, IOException {
    final UUID destDefId = UUID.randomUUID();
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition()
        .withDestinationDefinitionId(destDefId)
        .withName("random-destination-" + destDefId)
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withIcon("icon-3")
        .withSpec(new ConnectorSpecification())
        .withProtocolVersion(protocolVersion)
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
    configRepository.writeStandardDestinationDefinition(destDef);
    return destDef;
  }

  private SourceConnection createSourceConnection(final UUID workspaceId, final StandardSourceDefinition sourceDef)
      throws JsonValidationException, IOException {
    final UUID sourceId = UUID.randomUUID();
    final SourceConnection source = new SourceConnection()
        .withName("source-" + sourceId)
        .withTombstone(false)
        .withConfiguration(Jsons.deserialize("{}"))
        .withSourceDefinitionId(sourceDef.getSourceDefinitionId())
        .withWorkspaceId(workspaceId)
        .withSourceId(sourceId);
    configRepository.writeSourceConnectionNoSecrets(source);
    return source;
  }

  private DestinationConnection createDestinationConnection(final UUID workspaceId, final StandardDestinationDefinition destDef)
      throws JsonValidationException, IOException {
    final UUID destinationId = UUID.randomUUID();
    final DestinationConnection dest = new DestinationConnection()
        .withName("source-" + destinationId)
        .withTombstone(false)
        .withConfiguration(Jsons.deserialize("{}"))
        .withDestinationDefinitionId(destDef.getDestinationDefinitionId())
        .withWorkspaceId(workspaceId)
        .withDestinationId(destinationId);
    configRepository.writeDestinationConnectionNoSecrets(dest);
    return dest;
  }

  private StandardSync createStandardSync(final SourceConnection source, final DestinationConnection dest) throws IOException {
    final UUID connectionId = UUID.randomUUID();
    final StandardSync sync = new StandardSync()
        .withConnectionId(connectionId)
        .withSourceId(source.getSourceId())
        .withDestinationId(dest.getDestinationId())
        .withName("standard-sync-" + connectionId)
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withStatus(Status.ACTIVE)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false);
    standardSyncPersistence.writeStandardSync(sync);
    return sync;
  }

}
