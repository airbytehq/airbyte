/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.db.instance.configs.jooq.Keys.ACTOR_CATALOG_FETCH_EVENT__ACTOR_CATALOG_FETCH_EVENT_ACTOR_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.Keys.ACTOR__ACTOR_WORKSPACE_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.Keys.CONNECTION__CONNECTION_DESTINATION_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.Keys.CONNECTION__CONNECTION_SOURCE_ID_FKEY;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.Tables.WORKSPACE;
import static io.airbyte.db.instance.jobs.jooq.Tables.JOBS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.instance.configs.jooq.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.enums.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import io.airbyte.db.instance.configs.jooq.enums.StatusType;
import io.airbyte.db.instance.jobs.jooq.enums.JobStatus;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.UUID;
import javax.sql.DataSource;
import org.apache.commons.lang3.tuple.ImmutablePair;
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

  private static final UUID SRC_DEF_ID = UUID.randomUUID();
  private static final UUID DST_DEF_ID = UUID.randomUUID();

  private static Database configDb;

  @BeforeAll
  static void setUpAll() throws IOException, SQLException {
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

  @Nested
  class numJobs {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(JOBS).cascade().execute());
    }

    @Test
    void runningJobsShouldReturnCorrectCount() throws SQLException {
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.failed).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.running).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(4L, "", JobStatus.running).execute());

      final var res = configDb.query(MetricQueries::numberOfRunningJobs);
      assertEquals(2, res);
    }

    @Test
    void runningJobsShouldReturnZero() throws SQLException {
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::numberOfRunningJobs);
      assertEquals(0, res);
    }

    @Test
    void pendingJobsShouldReturnCorrectCount() throws SQLException {
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.failed).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(4L, "", JobStatus.running).execute());

      final var res = configDb.query(MetricQueries::numberOfPendingJobs);
      assertEquals(2, res);
    }

    @Test
    void pendingJobsShouldReturnZero() throws SQLException {
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.running).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::numberOfPendingJobs);
      assertEquals(0, res);
    }

  }

  @Nested
  class oldestPendingJob {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(JOBS).cascade().execute());
    }

    @Test
    @DisplayName("should return only the pending job's age in seconds")
    void shouldReturnOnlyPendingSeconds() throws SQLException {
      final var expAgeSecs = 1000;
      final var oldestCreateAt = OffsetDateTime.now().minus(expAgeSecs, ChronoUnit.SECONDS);
      // oldest pending job
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT).values(1L, "", JobStatus.pending, oldestCreateAt)
              .execute());
      // second oldest pending job
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT).values(2L, "", JobStatus.pending, OffsetDateTime.now())
              .execute());
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.running).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(4L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::oldestPendingJobAgeSecs);
      assertEquals(1000, res);
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.succeeded).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.running).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::oldestPendingJobAgeSecs);
      assertEquals(0L, res);
    }

  }

  @Nested
  class oldestRunningJob {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(JOBS).cascade().execute());
    }

    @Test
    @DisplayName("should return only the running job's age in seconds")
    void shouldReturnOnlyRunningSeconds() throws SQLException {
      final var expAgeSecs = 10000;
      final var oldestCreateAt = OffsetDateTime.now().minus(expAgeSecs, ChronoUnit.SECONDS);
      // oldest pending job
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT).values(1L, "", JobStatus.running, oldestCreateAt)
              .execute());
      // second oldest pending job
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT).values(2L, "", JobStatus.running, OffsetDateTime.now())
              .execute());
      // non-pending jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(4L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::oldestRunningJobAgeSecs);
      assertEquals(10000, res);
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.succeeded).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.pending).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.failed).execute());

      final var res = configDb.query(MetricQueries::oldestRunningJobAgeSecs);
      assertEquals(0L, res);
    }

  }

  @Nested
  class numActiveConnPerWorkspace {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(CONNECTION).cascade().execute());
      configDb.transaction(ctx -> ctx.truncate(ACTOR).cascade().execute());
      configDb.transaction(ctx -> ctx.truncate(WORKSPACE).cascade().execute());
    }

    @Test
    @DisplayName("should return only connections per workspace")
    void shouldReturnNumConnectionsBasic() throws SQLException {
      final var workspaceId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE).values(workspaceId, "test-0", false)
              .execute());

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx
              .insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
                  ACTOR.TOMBSTONE)
              .values(srcId, workspaceId, SRC_DEF_ID, "src", JSONB.valueOf("{}"), ActorType.source, false)
              .values(dstId, workspaceId, DST_DEF_ID, "dst", JSONB.valueOf("{}"), ActorType.destination, false)
              .execute());

      configDb.transaction(
          ctx -> ctx
              .insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
                  CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.active)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.active)
              .execute());

      final var res = configDb.query(MetricQueries::numberOfActiveConnPerWorkspace);
      assertEquals(1, res.size());
      assertEquals(2, res.get(0));
    }

    @Test
    @DisplayName("should ignore deleted connections")
    void shouldIgnoreNonRunningConnections() throws SQLException {
      final var workspaceId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE).values(workspaceId, "test-0", false)
              .execute());

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx
              .insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
                  ACTOR.TOMBSTONE)
              .values(srcId, workspaceId, SRC_DEF_ID, "src", JSONB.valueOf("{}"), ActorType.source, false)
              .values(dstId, workspaceId, DST_DEF_ID, "dst", JSONB.valueOf("{}"), ActorType.destination, false)
              .execute());

      configDb.transaction(
          ctx -> ctx
              .insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
                  CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.active)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.active)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.deprecated)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.inactive)
              .execute());

      final var res = configDb.query(MetricQueries::numberOfActiveConnPerWorkspace);
      assertEquals(1, res.size());
      assertEquals(2, res.get(0));
    }

    @Test
    @DisplayName("should ignore deleted connections")
    void shouldIgnoreDeletedWorkspaces() throws SQLException {
      final var workspaceId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE).values(workspaceId, "test-0", true)
              .execute());

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      configDb.transaction(
          ctx -> ctx
              .insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
                  ACTOR.TOMBSTONE)
              .values(srcId, workspaceId, SRC_DEF_ID, "src", JSONB.valueOf("{}"), ActorType.source, false)
              .values(dstId, workspaceId, DST_DEF_ID, "dst", JSONB.valueOf("{}"), ActorType.destination, false)
              .execute());

      configDb.transaction(
          ctx -> ctx
              .insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
                  CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
              .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, "conn", JSONB.valueOf("{}"), true, StatusType.active)
              .execute());

      final var res = configDb.query(MetricQueries::numberOfActiveConnPerWorkspace);
      assertEquals(0, res.size());
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var res = configDb.query(MetricQueries::numberOfActiveConnPerWorkspace);
      assertEquals(0, res.size());
    }

  }

  @Nested
  class overallJobRuntimeForTerminalJobsInLastHour {

    @AfterEach
    void tearDown() throws SQLException {
      configDb.transaction(ctx -> ctx.truncate(JOBS).cascade().execute());
    }

    @Test
    @DisplayName("should ignore non terminal jobs")
    void shouldIgnoreNonTerminalJobs() throws SQLException {
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.running).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.incomplete).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(3L, "", JobStatus.pending).execute());

      final var res = configDb.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      assertEquals(0, res.size());
    }

    @Test
    @DisplayName("should ignore jobs older than 1 hour")
    void shouldIgnoreJobsOlderThan1Hour() throws SQLException {
      final var updateAt = OffsetDateTime.now().minus(2, ChronoUnit.HOURS);
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.UPDATED_AT).values(1L, "", JobStatus.succeeded, updateAt).execute());

      final var res = configDb.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      assertEquals(0, res.size());
    }

    @Test
    @DisplayName("should return correct duration for terminal jobs")
    void shouldReturnTerminalJobs() throws SQLException {
      final var updateAt = OffsetDateTime.now();
      final var expAgeSecs = 10000;
      final var createAt = updateAt.minus(expAgeSecs, ChronoUnit.SECONDS);

      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(1L, "", JobStatus.succeeded, createAt, updateAt).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(2L, "", JobStatus.failed, createAt, updateAt).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(3L, "", JobStatus.cancelled, createAt, updateAt).execute());

      final var res = configDb.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      assertEquals(3, res.size());

      final var exp = List.of(
          new ImmutablePair<>(JobStatus.succeeded, expAgeSecs * 1.0),
          new ImmutablePair<>(JobStatus.cancelled, expAgeSecs * 1.0),
          new ImmutablePair<>(JobStatus.failed, expAgeSecs * 1.0));
      assertTrue(res.containsAll(exp) && exp.containsAll(res));
    }

    @Test
    @DisplayName("should return correct duration for jobs that terminated in the last hour")
    void shouldReturnTerminalJobsComplex() throws SQLException {
      final var updateAtNow = OffsetDateTime.now();
      final var expAgeSecs = 10000;
      final var createAt = updateAtNow.minus(expAgeSecs, ChronoUnit.SECONDS);

      // terminal jobs in last hour
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(1L, "", JobStatus.succeeded, createAt, updateAtNow).execute());
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(2L, "", JobStatus.failed, createAt, updateAtNow).execute());

      // old terminal jobs
      final var updateAtOld = OffsetDateTime.now().minus(2, ChronoUnit.HOURS);
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
              .values(3L, "", JobStatus.cancelled, createAt, updateAtOld).execute());

      // non-terminal jobs
      configDb.transaction(
          ctx -> ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT)
              .values(4L, "", JobStatus.running, createAt).execute());

      final var res = configDb.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      assertEquals(2, res.size());

      final var exp = List.of(
          new ImmutablePair<>(JobStatus.succeeded, expAgeSecs * 1.0),
          new ImmutablePair<>(JobStatus.failed, expAgeSecs * 1.0));
      assertTrue(res.containsAll(exp) && exp.containsAll(res));
    }

    @Test
    @DisplayName("should not error out or return any result if not applicable")
    void shouldReturnNothingIfNotApplicable() throws SQLException {
      final var res = configDb.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
      assertEquals(0, res.size());
    }

  }

}
