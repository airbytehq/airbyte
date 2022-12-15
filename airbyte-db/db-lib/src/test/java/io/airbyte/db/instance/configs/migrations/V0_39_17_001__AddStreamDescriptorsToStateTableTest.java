/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.migrations.V0_39_17_001__AddStreamDescriptorsToStateTable.StateType;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import java.util.UUID;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.exception.DataAccessException;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidDuplicateLiterals")
class V0_39_17_001__AddStreamDescriptorsToStateTableTest extends AbstractConfigsDatabaseTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_39_17_001__AddStreamDescriptorsToStateTableTest.class);
  private final String STATE_TABLE = "State";

  private UUID connection1;
  private UUID connection2;

  @Test
  void testSimpleMigration() {
    final DSLContext context = getDslContext();

    // Adding a couple of states
    context.insertInto(DSL.table(STATE_TABLE))
        .columns(
            DSL.field("id"),
            DSL.field("connection_id"))
        .values(UUID.randomUUID(), connection1)
        .values(UUID.randomUUID(), connection2)
        .execute();

    // Preconditions check: we should have one row in state
    Assertions.assertEquals(2, context.select().from(STATE_TABLE).execute());

    // Applying the migration
    devConfigsDbMigrator.migrate();

    final UUID newState = UUID.randomUUID();
    context.insertInto(DSL.table(STATE_TABLE))
        .columns(
            DSL.field("id"),
            DSL.field("connection_id"),
            DSL.field("stream_name"))
        .values(newState, connection1, "new_stream")
        .execute();

    LOGGER.info(String.valueOf(context.selectFrom("connection").fetch()));
    LOGGER.info(String.valueOf(context.selectFrom(STATE_TABLE).fetch()));

    // Our two initial rows and the new row should be LEGACY
    Assertions.assertEquals(3,
        context.select()
            .from(STATE_TABLE)
            .where(DSL.field("type").equal(StateType.LEGACY))
            .execute());

    // There should be no STREAM or GLOBAL
    Assertions.assertEquals(0,
        context.select()
            .from(STATE_TABLE)
            .where(DSL.field("type").in(StateType.GLOBAL, StateType.STREAM))
            .execute());
  }

  @Test
  void testUniquenessConstraint() {
    devConfigsDbMigrator.migrate();

    final DSLContext context = getDslContext();
    context.insertInto(DSL.table(STATE_TABLE))
        .columns(
            DSL.field("id"),
            DSL.field("connection_id"),
            DSL.field("type"),
            DSL.field("stream_name"),
            DSL.field("namespace"))
        .values(UUID.randomUUID(), connection1, StateType.GLOBAL, "stream1", "ns2")
        .execute();

    context.insertInto(DSL.table(STATE_TABLE))
        .columns(
            DSL.field("id"),
            DSL.field("connection_id"),
            DSL.field("type"),
            DSL.field("stream_name"),
            DSL.field("namespace"))
        .values(UUID.randomUUID(), connection1, StateType.GLOBAL, "stream1", "ns1")
        .execute();

    context.insertInto(DSL.table(STATE_TABLE))
        .columns(
            DSL.field("id"),
            DSL.field("connection_id"),
            DSL.field("type"),
            DSL.field("stream_name"),
            DSL.field("namespace"))
        .values(UUID.randomUUID(), connection1, StateType.GLOBAL, "stream2", "ns2")
        .execute();

    Assertions.assertThrows(DataAccessException.class, () -> {
      context.insertInto(DSL.table(STATE_TABLE))
          .columns(
              DSL.field("id"),
              DSL.field("connection_id"),
              DSL.field("type"),
              DSL.field("stream_name"),
              DSL.field("namespace"))
          .values(UUID.randomUUID(), connection1, StateType.GLOBAL, "stream1", "ns2")
          .execute();
    });
  }

  @BeforeEach
  void beforeEach() {
    final Flyway flyway =
        FlywayFactory.create(dataSource, "V0_39_17_001__AddStreamDescriptorsToStateTableTest", ConfigsDatabaseMigrator.DB_IDENTIFIER,
            ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final ConfigsDatabaseMigrator configsDbMigrator = new ConfigsDatabaseMigrator(database, flyway);
    devConfigsDbMigrator = new DevDatabaseMigrator(configsDbMigrator);

    devConfigsDbMigrator.createBaseline();
    injectMockData();
  }

  @AfterEach
  void afterEach() {
    // Making sure we reset between tests
    dslContext.dropSchemaIfExists("public").cascade().execute();
    dslContext.createSchema("public").execute();
    dslContext.setSchema("public").execute();
  }

  private void injectMockData() {
    final DSLContext context = getDslContext();

    final UUID workspaceId = UUID.randomUUID();
    final UUID actorId = UUID.randomUUID();
    final UUID actorDefinitionId = UUID.randomUUID();
    connection1 = UUID.randomUUID();
    connection2 = UUID.randomUUID();

    context.insertInto(DSL.table("workspace"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("slug"),
            DSL.field("initial_setup_complete"))
        .values(
            workspaceId,
            "base workspace",
            "base_workspace",
            true)
        .execute();
    context.insertInto(DSL.table("actor_definition"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("docker_repository"),
            DSL.field("docker_image_tag"),
            DSL.field("actor_type"),
            DSL.field("spec"))
        .values(
            actorDefinitionId,
            "Jenkins",
            "farosai/airbyte-jenkins-source",
            "0.1.23",
            ActorType.source,
            JSONB.valueOf("{}"))
        .execute();
    context.insertInto(DSL.table("actor"))
        .columns(
            DSL.field("id"),
            DSL.field("workspace_id"),
            DSL.field("actor_definition_id"),
            DSL.field("name"),
            DSL.field("configuration"),
            DSL.field("actor_type"))
        .values(
            actorId,
            workspaceId,
            actorDefinitionId,
            "ActorName",
            JSONB.valueOf("{}"),
            ActorType.source)
        .execute();

    insertConnection(context, connection1, actorId);
    insertConnection(context, connection2, actorId);
  }

  private void insertConnection(final DSLContext context, final UUID connectionId, final UUID actorId) {
    context.insertInto(DSL.table("connection"))
        .columns(
            DSL.field("id"),
            DSL.field("namespace_definition"),
            DSL.field("source_id"),
            DSL.field("destination_id"),
            DSL.field("name"),
            DSL.field("catalog"),
            DSL.field("manual"))
        .values(
            connectionId,
            NamespaceDefinitionType.source,
            actorId,
            actorId,
            "Connection" + connectionId.toString(),
            JSONB.valueOf("{}"),
            true)
        .execute();
  }

  private DevDatabaseMigrator devConfigsDbMigrator;

}
