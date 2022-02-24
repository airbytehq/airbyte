/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.llib;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.jooq.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.metrics.lib.MetricsQueries;
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

  private static PostgreSQLContainer<?> container;
  private static Database configDb;
  private static DatabaseConfigPersistence configPersistence;

  @BeforeAll
  static void setUpAll() throws IOException {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withUsername(USER)
        .withPassword(PASS);
    container.start();

    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(container);
    configDb = databaseProviders.createNewConfigsDatabase();
    new DatabaseConfigPersistence(configDb);
  }

  @Nested
  class srcIdAndDestIdToReleaseStages {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(ACTOR));
      configDb.transaction(ctx -> ctx.truncate(ACTOR_DEFINITION));
    }

    @Test
    @DisplayName("should return the right release stages")
    public void shouldReturnReleaseStages() throws SQLException {
      final var srcDefId = UUID.randomUUID();
      final var dstDefId = UUID.randomUUID();
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();

      // create src and dst def
      configDb.transaction(ctx -> ctx
          .insertInto(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, ACTOR_DEFINITION.NAME, ACTOR_DEFINITION.DOCKER_REPOSITORY,
              ACTOR_DEFINITION.DOCKER_IMAGE_TAG, ACTOR_DEFINITION.SPEC, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.RELEASE_STAGE)
          .values(srcDefId, "srcDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.source, ReleaseStage.beta)
          .values(dstDefId, "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.generally_available)
          .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.alpha).execute());
      // drop foreign key to simplify set up
      configDb.transaction(ctx -> ctx.alterTable(ACTOR).dropForeignKey("actor_workspace_id_fkey").execute());
      // create src and dst
      configDb.transaction(
          ctx -> ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
              .values(srcId, UUID.randomUUID(), srcDefId, "src", JSONB.valueOf("{}"), ActorType.source)
              .values(dstId, UUID.randomUUID(), dstDefId, "dst", JSONB.valueOf("{}"), ActorType.destination)
              .execute());
      final var res = configDb.query(ctx -> MetricsQueries.srcIdAndDestIdToReleaseStages(ctx, srcId, dstId));
      assertEquals(List.of(ReleaseStage.beta, ReleaseStage.generally_available), res);
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    public void shouldReturnNothingIfNotApplicable() throws SQLException {
      configDb.transaction(ctx -> ctx
          .insertInto(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, ACTOR_DEFINITION.NAME, ACTOR_DEFINITION.DOCKER_REPOSITORY,
              ACTOR_DEFINITION.DOCKER_IMAGE_TAG, ACTOR_DEFINITION.SPEC, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.RELEASE_STAGE)
          .values(UUID.randomUUID(), "srcDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.source, ReleaseStage.beta)
          .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.generally_available)
          .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.alpha).execute());

      final var res = configDb.query(ctx -> MetricsQueries.srcIdAndDestIdToReleaseStages(ctx, UUID.randomUUID(), UUID.randomUUID()));
      assertEquals(0, res.size());
    }

  }

}
