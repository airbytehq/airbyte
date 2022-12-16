/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.generated.Keys.ACTOR_CATALOG_FETCH_EVENT__ACTOR_CATALOG_FETCH_EVENT_ACTOR_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.generated.Keys.ACTOR__ACTOR_WORKSPACE_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.generated.Keys.CONNECTION__CONNECTION_DESTINATION_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.generated.Keys.CONNECTION__CONNECTION_SOURCE_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.configs.jooq.generated.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class MetricsQueriesTest {

  private static final String USER = "user";
  private static final String PASS = "hunter2";
  private static final String SRC = "src";
  private static final String DEST = "dst";
  private static final String DISPLAY_NAME = "should not error out or return any result if not applicable";
  private static final String CONN = "conn";

  private static final UUID SRC_DEF_ID = UUID.randomUUID();
  private static final UUID DST_DEF_ID = UUID.randomUUID();

  private static Database configDb;

  @BeforeAll
  static void setUpAll() throws IOException, SQLException, DatabaseInitializationException {
    final PostgreSQLContainer<?> container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withUsername(USER)
        .withPassword(PASS);
    container.start();

    final DataSource dataSource = DatabaseConnectionHelper.createDataSource(container);
    final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(dataSource, dslContext);
    configDb = databaseProviders.createNewConfigsDatabase();
    databaseProviders.createNewJobsDatabase();

    // create src and dst def
    configDb.transaction(ctx -> ctx
        .insertInto(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, ACTOR_DEFINITION.NAME, ACTOR_DEFINITION.DOCKER_REPOSITORY,
            ACTOR_DEFINITION.DOCKER_IMAGE_TAG, ACTOR_DEFINITION.SPEC, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.RELEASE_STAGE)
        .values(SRC_DEF_ID, "srcDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.source, ReleaseStage.beta)
        .values(DST_DEF_ID, "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.generally_available)
        .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.alpha).execute());

    // drop constraints to simplify test set up
    configDb.transaction(ctx -> ctx.alterTable(ACTOR).dropForeignKey(ACTOR__ACTOR_WORKSPACE_ID_FKEY.constraint()).execute());
    configDb.transaction(ctx -> ctx.alterTable(CONNECTION).dropForeignKey(CONNECTION__CONNECTION_DESTINATION_ID_FKEY.constraint()).execute());
    configDb.transaction(ctx -> ctx.alterTable(CONNECTION).dropForeignKey(CONNECTION__CONNECTION_SOURCE_ID_FKEY.constraint()).execute());
    configDb.transaction(ctx -> ctx.alterTable(ACTOR_CATALOG_FETCH_EVENT)
        .dropForeignKey(ACTOR_CATALOG_FETCH_EVENT__ACTOR_CATALOG_FETCH_EVENT_ACTOR_ID_FKEY.constraint()).execute());
    configDb.transaction(ctx -> ctx.alterTable(WORKSPACE).alter(WORKSPACE.SLUG).dropNotNull().execute());
    configDb.transaction(ctx -> ctx.alterTable(WORKSPACE).alter(WORKSPACE.INITIAL_SETUP_COMPLETE).dropNotNull().execute());
  }

  @Nested
  class srcIdAndDestIdToReleaseStages {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(ACTOR).execute());
      configDb.transaction(ctx -> ctx.truncate(JOBS).execute());
    }

    @Test
    @DisplayName("should return the right release stages")
    void shouldReturnReleaseStages() throws SQLException {
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();

      // create src and dst
      configDb.transaction(
          ctx -> ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
              .values(srcId, UUID.randomUUID(), SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source)
              .values(dstId, UUID.randomUUID(), DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination)
              .execute());
      final var res = configDb.query(ctx -> MetricQueries.srcIdAndDestIdToReleaseStages(ctx, srcId, dstId));
      assertEquals(List.of(ReleaseStage.beta, ReleaseStage.generally_available), res);
    }

    @Test
    @DisplayName(DISPLAY_NAME)
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var res = configDb.query(ctx -> MetricQueries.srcIdAndDestIdToReleaseStages(ctx, UUID.randomUUID(), UUID.randomUUID()));
      assertEquals(0, res.size());
    }

  }

  @Nested
  class jobIdToReleaseStages {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(ACTOR).execute());
      configDb.transaction(ctx -> ctx.truncate(JOBS).execute());
    }

    @Test
    @DisplayName("should return the right release stages")
    void shouldReturnReleaseStages() throws SQLException {
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      // create src and dst
      configDb.transaction(
          ctx -> ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
              .values(srcId, UUID.randomUUID(), SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source)
              .values(dstId, UUID.randomUUID(), DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination)
              .execute());
      final var connId = UUID.randomUUID();
      // create connection
      configDb.transaction(
          ctx -> ctx
              .insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
                  CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL)
              .values(connId, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true)
              .execute());
      // create job
      final var jobId = 1L;
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE).values(jobId, connId.toString()).execute());

      final var res = configDb.query(ctx -> MetricQueries.jobIdToReleaseStages(ctx, jobId));
      assertEquals(List.of(ReleaseStage.beta, ReleaseStage.generally_available), res);
    }

    @Test
    @DisplayName(DISPLAY_NAME)
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var missingJobId = 100000L;
      final var res = configDb.query(ctx -> MetricQueries.jobIdToReleaseStages(ctx, missingJobId));
      assertEquals(0, res.size());
    }

  }

}
