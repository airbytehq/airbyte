/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION;
import static io.airbyte.db.instance.jobs.jooq.Tables.*;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.jooq.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.enums.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.UUID;
import org.jooq.JSONB;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class MetrisQueriesTest {

  private static final String USER = "user";
  private static final String PASS = "hunter2";

  private static final UUID SRC_DEF_ID = UUID.randomUUID();
  private static final UUID DST_DEF_ID = UUID.randomUUID();

  private static PostgreSQLContainer<?> container;
  private static Database configDb;

  @BeforeAll
  static void setUpAll() throws IOException, SQLException {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withUsername(USER)
        .withPassword(PASS);
    container.start();

    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(container);
    configDb = databaseProviders.createNewConfigsDatabase();
    databaseProviders.createNewJobsDatabase();

    // create src and dst def
    configDb.transaction(ctx -> ctx
        .insertInto(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, ACTOR_DEFINITION.NAME, ACTOR_DEFINITION.DOCKER_REPOSITORY,
            ACTOR_DEFINITION.DOCKER_IMAGE_TAG, ACTOR_DEFINITION.SPEC, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.RELEASE_STAGE)
        .values(SRC_DEF_ID, "srcDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.source, ReleaseStage.beta)
        .values(DST_DEF_ID, "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.generally_available)
        .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.alpha).execute());

    // drop the constraint to simplify following test set up
    configDb.transaction(ctx -> ctx.alterTable(ACTOR).dropForeignKey("actor_workspace_id_fkey").execute());
  }

  @AfterEach
  void tearDown() throws SQLException {
    configDb.transaction(ctx -> ctx.truncate(ACTOR));
  }

  @Nested
  class srcIdAndDestIdToReleaseStages {

    @Test
    @DisplayName("should return the right release stages")
    void shouldReturnReleaseStages() throws SQLException {
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();

      // create src and dst
      configDb.transaction(
          ctx -> ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
              .values(srcId, UUID.randomUUID(), SRC_DEF_ID, "src", JSONB.valueOf("{}"), ActorType.source)
              .values(dstId, UUID.randomUUID(), DST_DEF_ID, "dst", JSONB.valueOf("{}"), ActorType.destination)
              .execute());
      final var res = configDb.query(ctx -> MetricQueries.srcIdAndDestIdToReleaseStages(ctx, srcId, dstId));
      assertEquals(List.of(ReleaseStage.beta, ReleaseStage.generally_available), res);
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var res = configDb.query(ctx -> MetricQueries.srcIdAndDestIdToReleaseStages(ctx, UUID.randomUUID(), UUID.randomUUID()));
      assertEquals(0, res.size());
    }

  }

  @Nested
  class jobIdToReleaseStages {

    @Test
    @DisplayName("should return the right release stages")
    void shouldReturnReleaseStages() throws SQLException {
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      // create src and dst
      configDb.transaction(
          ctx -> ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
              .values(srcId, UUID.randomUUID(), SRC_DEF_ID, "src", JSONB.valueOf("{}"), ActorType.source)
              .values(dstId, UUID.randomUUID(), DST_DEF_ID, "dst", JSONB.valueOf("{}"), ActorType.destination)
              .execute());
      final var connId = UUID.randomUUID();
      // create connection
      configDb.transaction(
          ctx -> ctx
              .insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
                  CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL)
              .values(connId, NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true)
              .execute());
      // create job
      final var jobId = 1L;
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE).values(jobId, connId.toString()).execute());

      final var res = configDb.query(ctx -> MetricQueries.jobIdToReleaseStages(ctx, jobId));
      assertEquals(List.of(ReleaseStage.beta, ReleaseStage.generally_available), res);
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var missingJobId = 100000L;
      final var res = configDb.query(ctx -> MetricQueries.jobIdToReleaseStages(ctx, missingJobId));
      assertEquals(0, res.size());
    }

  }

}
