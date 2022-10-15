/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

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
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.configs.jooq.generated.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.generated.enums.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.configs.jooq.generated.enums.StatusType;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobConfigType;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class MetricRepositoryTest {

  private static final String SRC = "src";
  private static final String DEST = "dst";
  private static final String CONN = "conn";
  private static final UUID SRC_DEF_ID = UUID.randomUUID();
  private static final UUID DST_DEF_ID = UUID.randomUUID();
  private static MetricRepository db;
  private static DSLContext ctx;

  @BeforeAll
  public static void setUpAll() throws DatabaseInitializationException, IOException {
    final var psqlContainer = new PostgreSQLContainer<>("postgres:13-alpine")
        .withUsername("user")
        .withPassword("hunter2");
    psqlContainer.start();

    final var dataSource = DatabaseConnectionHelper.createDataSource(psqlContainer);
    ctx = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    final var dbProviders = new TestDatabaseProviders(dataSource, ctx);
    dbProviders.createNewConfigsDatabase();
    dbProviders.createNewJobsDatabase();

    ctx.insertInto(ACTOR_DEFINITION, ACTOR_DEFINITION.ID, ACTOR_DEFINITION.NAME, ACTOR_DEFINITION.DOCKER_REPOSITORY,
        ACTOR_DEFINITION.DOCKER_IMAGE_TAG, ACTOR_DEFINITION.SPEC, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.RELEASE_STAGE)
        .values(SRC_DEF_ID, "srcDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.source, ReleaseStage.beta)
        .values(DST_DEF_ID, "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.generally_available)
        .values(UUID.randomUUID(), "dstDef", "repository", "tag", JSONB.valueOf("{}"), ActorType.destination, ReleaseStage.alpha)
        .execute();

    // drop constraints to simplify test set up
    ctx.alterTable(ACTOR).dropForeignKey(ACTOR__ACTOR_WORKSPACE_ID_FKEY.constraint()).execute();
    ctx.alterTable(CONNECTION).dropForeignKey(CONNECTION__CONNECTION_DESTINATION_ID_FKEY.constraint()).execute();
    ctx.alterTable(CONNECTION).dropForeignKey(CONNECTION__CONNECTION_SOURCE_ID_FKEY.constraint()).execute();
    ctx.alterTable(ACTOR_CATALOG_FETCH_EVENT)
        .dropForeignKey(ACTOR_CATALOG_FETCH_EVENT__ACTOR_CATALOG_FETCH_EVENT_ACTOR_ID_FKEY.constraint()).execute();
    ctx.alterTable(WORKSPACE).alter(WORKSPACE.SLUG).dropNotNull().execute();
    ctx.alterTable(WORKSPACE).alter(WORKSPACE.INITIAL_SETUP_COMPLETE).dropNotNull().execute();

    db = new MetricRepository(ctx);
  }

  @BeforeEach
  void setUp() {
    ctx.truncate(ACTOR).execute();
    ctx.truncate(CONNECTION).cascade().execute();
    ctx.truncate(JOBS).cascade().execute();
    ctx.truncate(WORKSPACE).cascade().execute();
  }

  @AfterEach
  void tearDown() {

  }

  @Nested
  class NumJobs {

    @Test
    void shouldReturnReleaseStages() {
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();

      ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE)
          .values(srcId, UUID.randomUUID(), SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source)
          .values(dstId, UUID.randomUUID(), DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination)
          .execute();

      final var activeConnectionId = UUID.randomUUID();
      final var inactiveConnectionId = UUID.randomUUID();
      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.STATUS, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID,
          CONNECTION.DESTINATION_ID, CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL)
          .values(activeConnectionId, StatusType.active, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true)
          .values(inactiveConnectionId, StatusType.inactive, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true)
          .execute();

      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, activeConnectionId.toString(), JobStatus.pending)
          .execute();
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(2L, activeConnectionId.toString(), JobStatus.failed)
          .values(3L, activeConnectionId.toString(), JobStatus.running)
          .values(4L, activeConnectionId.toString(), JobStatus.running)
          .values(5L, inactiveConnectionId.toString(), JobStatus.running)
          .execute();

      assertEquals(2, db.numberOfRunningJobs());
      assertEquals(1, db.numberOfOrphanRunningJobs());
    }

    @Test
    void runningJobsShouldReturnZero() throws SQLException {
      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(1L, "", JobStatus.pending).execute();
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS).values(2L, "", JobStatus.failed).execute();

      final var res = db.numberOfRunningJobs();
      assertEquals(0, res);
    }

    @Test
    void pendingJobsShouldReturnCorrectCount() throws SQLException {
      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, "", JobStatus.pending)
          .values(2L, "", JobStatus.failed)
          .values(3L, "", JobStatus.pending)
          .values(4L, "", JobStatus.running)
          .execute();

      final var res = db.numberOfPendingJobs();
      assertEquals(2, res);
    }

    @Test
    void pendingJobsShouldReturnZero() throws SQLException {
      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, "", JobStatus.running)
          .values(2L, "", JobStatus.failed)
          .execute();

      final var res = db.numberOfPendingJobs();
      assertEquals(0, res);
    }

  }

  @Nested
  class OldestPendingJob {

    @Test
    void shouldReturnOnlyPendingSeconds() throws SQLException {
      final var expAgeSecs = 1000;
      final var oldestCreateAt = OffsetDateTime.now().minus(expAgeSecs, ChronoUnit.SECONDS);

      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT)
          // oldest pending job
          .values(1L, "", JobStatus.pending, oldestCreateAt)
          // second-oldest pending job
          .values(2L, "", JobStatus.pending, OffsetDateTime.now())
          .execute();
      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(3L, "", JobStatus.running)
          .values(4L, "", JobStatus.failed)
          .execute();

      final var res = db.oldestPendingJobAgeSecs();
      // expected age is 1000 seconds, but allow for +/- 1 second to account for timing/rounding errors
      assertTrue(List.of(999L, 1000L, 1001L).contains(res));
    }

    @Test
    void shouldReturnNothingIfNotApplicable() {
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, "", JobStatus.succeeded)
          .values(2L, "", JobStatus.running)
          .values(3L, "", JobStatus.failed).execute();

      final var res = db.oldestPendingJobAgeSecs();
      assertEquals(0L, res);
    }

  }

  @Nested
  class OldestRunningJob {

    @Test
    void shouldReturnOnlyRunningSeconds() {
      final var expAgeSecs = 10000;
      final var oldestCreateAt = OffsetDateTime.now().minus(expAgeSecs, ChronoUnit.SECONDS);

      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT)
          // oldest pending job
          .values(1L, "", JobStatus.running, oldestCreateAt)
          // second-oldest pending job
          .values(2L, "", JobStatus.running, OffsetDateTime.now())
          .execute();

      // non-pending jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(3L, "", JobStatus.pending)
          .values(4L, "", JobStatus.failed)
          .execute();

      final var res = db.oldestRunningJobAgeSecs();
      // expected age is 10000 seconds, but allow for +/- 1 second to account for timing/rounding errors
      assertTrue(List.of(9999L, 10000L, 10001L).contains(res));
    }

    @Test
    void shouldReturnNothingIfNotApplicable() {
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, "", JobStatus.succeeded)
          .values(2L, "", JobStatus.pending)
          .values(3L, "", JobStatus.failed)
          .execute();

      final var res = db.oldestRunningJobAgeSecs();
      assertEquals(0L, res);
    }

  }

  @Nested
  class NumActiveConnsPerWorkspace {

    @Test
    void shouldReturnNumConnectionsBasic() {
      final var workspaceId = UUID.randomUUID();
      ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE)
          .values(workspaceId, "test-0", false)
          .execute();

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
          ACTOR.TOMBSTONE)
          .values(srcId, workspaceId, SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source, false)
          .values(dstId, workspaceId, DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination, false)
          .execute();

      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
          CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.active)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.active)
          .execute();

      final var res = db.numberOfActiveConnPerWorkspace();
      assertEquals(1, res.size());
      assertEquals(2, res.get(0));
    }

    @Test
    @DisplayName("should ignore deleted connections")
    void shouldIgnoreNonRunningConnections() {
      final var workspaceId = UUID.randomUUID();
      ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE)
          .values(workspaceId, "test-0", false)
          .execute();

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
          ACTOR.TOMBSTONE)
          .values(srcId, workspaceId, SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source, false)
          .values(dstId, workspaceId, DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination, false)
          .execute();

      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
          CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.active)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.active)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.deprecated)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.inactive)
          .execute();

      final var res = db.numberOfActiveConnPerWorkspace();
      assertEquals(1, res.size());
      assertEquals(2, res.get(0));
    }

    @Test
    @DisplayName("should ignore deleted connections")
    void shouldIgnoreDeletedWorkspaces() {
      final var workspaceId = UUID.randomUUID();
      ctx.insertInto(WORKSPACE, WORKSPACE.ID, WORKSPACE.NAME, WORKSPACE.TOMBSTONE)
          .values(workspaceId, "test-0", true)
          .execute();

      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      ctx.insertInto(ACTOR, ACTOR.ID, ACTOR.WORKSPACE_ID, ACTOR.ACTOR_DEFINITION_ID, ACTOR.NAME, ACTOR.CONFIGURATION, ACTOR.ACTOR_TYPE,
          ACTOR.TOMBSTONE)
          .values(srcId, workspaceId, SRC_DEF_ID, SRC, JSONB.valueOf("{}"), ActorType.source, false)
          .values(dstId, workspaceId, DST_DEF_ID, DEST, JSONB.valueOf("{}"), ActorType.destination, false)
          .execute();

      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
          CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.MANUAL, CONNECTION.STATUS)
          .values(UUID.randomUUID(), NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"), true, StatusType.active)
          .execute();

      final var res = db.numberOfActiveConnPerWorkspace();
      assertEquals(0, res.size());
    }

    @Test
    void shouldReturnNothingIfNotApplicable() {
      final var res = db.numberOfActiveConnPerWorkspace();
      assertEquals(0, res.size());
    }

  }

  @Nested
  class OverallJobRuntimeForTerminalJobsInLastHour {

    @Test
    void shouldIgnoreNonTerminalJobs() throws SQLException {
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS)
          .values(1L, "", JobStatus.running)
          .values(2L, "", JobStatus.incomplete)
          .values(3L, "", JobStatus.pending)
          .execute();

      final var res = db.overallJobRuntimeForTerminalJobsInLastHour();
      assertEquals(0, res.size());
    }

    @Test
    void shouldIgnoreJobsOlderThan1Hour() {
      final var updateAt = OffsetDateTime.now().minus(2, ChronoUnit.HOURS);
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.UPDATED_AT).values(1L, "", JobStatus.succeeded, updateAt).execute();

      final var res = db.overallJobRuntimeForTerminalJobsInLastHour();
      assertEquals(0, res.size());
    }

    @Test
    @DisplayName("should return correct duration for terminal jobs")
    void shouldReturnTerminalJobs() {
      final var updateAt = OffsetDateTime.now();
      final var expAgeSecs = 10000;
      final var createAt = updateAt.minus(expAgeSecs, ChronoUnit.SECONDS);

      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(1L, "", JobStatus.succeeded, createAt, updateAt)
          .execute();
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(2L, "", JobStatus.failed, createAt, updateAt)
          .execute();
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(3L, "", JobStatus.cancelled, createAt, updateAt)
          .execute();

      final var res = db.overallJobRuntimeForTerminalJobsInLastHour();
      assertEquals(3, res.size());

      final var exp = Map.of(
          JobStatus.succeeded, expAgeSecs * 1.0,
          JobStatus.cancelled, expAgeSecs * 1.0,
          JobStatus.failed, expAgeSecs * 1.0);
      assertEquals(exp, res);
    }

    @Test
    void shouldReturnTerminalJobsComplex() {
      final var updateAtNow = OffsetDateTime.now();
      final var expAgeSecs = 10000;
      final var createAt = updateAtNow.minus(expAgeSecs, ChronoUnit.SECONDS);

      // terminal jobs in last hour
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(1L, "", JobStatus.succeeded, createAt, updateAtNow)
          .execute();
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(2L, "", JobStatus.failed, createAt, updateAtNow)
          .execute();

      // old terminal jobs
      final var updateAtOld = OffsetDateTime.now().minus(2, ChronoUnit.HOURS);
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT)
          .values(3L, "", JobStatus.cancelled, createAt, updateAtOld)
          .execute();

      // non-terminal jobs
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT)
          .values(4L, "", JobStatus.running, createAt)
          .execute();

      final var res = db.overallJobRuntimeForTerminalJobsInLastHour();
      assertEquals(2, res.size());

      final var exp = Map.of(
          JobStatus.succeeded, expAgeSecs * 1.0,
          JobStatus.failed, expAgeSecs * 1.0);
      assertEquals(exp, res);
    }

    @Test
    void shouldReturnNothingIfNotApplicable() {
      final var res = db.overallJobRuntimeForTerminalJobsInLastHour();
      assertEquals(0, res.size());
    }

  }

  @Nested
  class AbnormalJobsInLastDay {

    @Test
    void shouldCountInJobsWithMissingRun() throws SQLException {
      final var updateAt = OffsetDateTime.now().minus(300, ChronoUnit.HOURS);
      final var connectionId = UUID.randomUUID();
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      final var syncConfigType = JobConfigType.sync;

      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
          CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.SCHEDULE, CONNECTION.MANUAL, CONNECTION.STATUS, CONNECTION.CREATED_AT,
          CONNECTION.UPDATED_AT)
          .values(connectionId, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"),
              JSONB.valueOf("{\"units\": 6, \"timeUnit\": \"hours\"}"), false, StatusType.active, updateAt, updateAt)
          .execute();

      // Jobs running in prior day will not be counted
      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT, JOBS.CONFIG_TYPE)
          .values(100L, connectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(28, ChronoUnit.HOURS), updateAt, syncConfigType)
          .values(1L, connectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(20, ChronoUnit.HOURS), updateAt, syncConfigType)
          .values(2L, connectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(10, ChronoUnit.HOURS), updateAt, syncConfigType)
          .values(3L, connectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(5, ChronoUnit.HOURS), updateAt, syncConfigType)
          .execute();

      final var totalConnectionResult = db.numScheduledActiveConnectionsInLastDay();
      assertEquals(1, totalConnectionResult);

      final var abnormalConnectionResult = db.numberOfJobsNotRunningOnScheduleInLastDay();
      assertEquals(1, abnormalConnectionResult);
    }

    @Test
    void shouldNotCountNormalJobsInAbnormalMetric() {
      final var updateAt = OffsetDateTime.now().minus(300, ChronoUnit.HOURS);
      final var inactiveConnectionId = UUID.randomUUID();
      final var activeConnectionId = UUID.randomUUID();
      final var srcId = UUID.randomUUID();
      final var dstId = UUID.randomUUID();
      final var syncConfigType = JobConfigType.sync;

      ctx.insertInto(CONNECTION, CONNECTION.ID, CONNECTION.NAMESPACE_DEFINITION, CONNECTION.SOURCE_ID, CONNECTION.DESTINATION_ID,
          CONNECTION.NAME, CONNECTION.CATALOG, CONNECTION.SCHEDULE, CONNECTION.MANUAL, CONNECTION.STATUS, CONNECTION.CREATED_AT,
          CONNECTION.UPDATED_AT)
          .values(inactiveConnectionId, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"),
              JSONB.valueOf("{\"units\": 12, \"timeUnit\": \"hours\"}"), false, StatusType.inactive, updateAt, updateAt)
          .values(activeConnectionId, NamespaceDefinitionType.source, srcId, dstId, CONN, JSONB.valueOf("{}"),
              JSONB.valueOf("{\"units\": 12, \"timeUnit\": \"hours\"}"), false, StatusType.active, updateAt, updateAt)
          .execute();

      ctx.insertInto(JOBS, JOBS.ID, JOBS.SCOPE, JOBS.STATUS, JOBS.CREATED_AT, JOBS.UPDATED_AT, JOBS.CONFIG_TYPE)
          .values(1L, activeConnectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(20, ChronoUnit.HOURS), updateAt,
              syncConfigType)
          .values(2L, activeConnectionId.toString(), JobStatus.succeeded, OffsetDateTime.now().minus(10, ChronoUnit.HOURS), updateAt,
              syncConfigType)
          .execute();

      final var totalConnectionResult = db.numScheduledActiveConnectionsInLastDay();
      assertEquals(1, totalConnectionResult);

      final var abnormalConnectionResult = db.numberOfJobsNotRunningOnScheduleInLastDay();
      assertEquals(0, abnormalConnectionResult);
    }

  }

}
