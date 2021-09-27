/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import javax.annotation.Nullable;
import org.flywaydb.core.api.configuration.Configuration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.InsertSetMoreStep;
import org.jooq.JSONB;
import org.jooq.Table;
import org.jooq.Typed;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class V0_29_21_001__Store_last_sync_state_test extends AbstractConfigsDatabaseTest {

  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();

  private static final Table<?> JOBS_TABLE = table("jobs");
  private static final Field<Long> JOB_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<String> JOB_SCOPE_FIELD = field("scope", SQLDataType.VARCHAR);

  private static final Table<?> ATTEMPTS_TABLE = table("attempts");
  private static final Field<Long> ATTEMPT_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<Long> ATTEMPT_JOB_ID_FIELD = field("job_id", SQLDataType.BIGINT);
  private static final Field<Integer> ATTEMPT_NUMBER_FIELD = field("attempt_number", SQLDataType.INTEGER);
  private static final Field<JSONB> ATTEMPT_OUTPUT_FIELD = field("output", SQLDataType.JSONB);

  private static final UUID SYNC_1_ID = UUID.randomUUID();
  private static final UUID SYNC_2_ID = UUID.randomUUID();
  private static final UUID SYNC_3_ID = UUID.randomUUID();
  private static final JsonNode SYNC_2_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 2222 } }");
  private static final JsonNode SYNC_3_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 3333 } }");

  private static Database jobDatabase;

  @BeforeAll
  public static void setupJobDatabase() throws Exception {
    jobDatabase = new JobsDatabaseInstance(
        container.getUsername(),
        container.getPassword(),
        container.getJdbcUrl())
            .getAndInitialize();
  }

  @Test
  @Order(10)
  public void testGetJobsDatabase() {
    // when there is no database environment variable, the return value is empty
    assertTrue(V0_29_21_001__Store_last_sync_state.getJobsDatabase(new EnvConfigs()).isEmpty());

    // when there is database environment variable, return the database
    final Configs configs = mock(Configs.class);
    when(configs.getDatabaseUser()).thenReturn(container.getUsername());
    when(configs.getDatabasePassword()).thenReturn(container.getPassword());
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());

    assertTrue(V0_29_21_001__Store_last_sync_state.getJobsDatabase(configs).isPresent());
  }

  @Test
  @Order(20)
  public void testGetSyncToStateMap() throws Exception {
    jobDatabase.query(ctx -> {
      // Create three jobs for three standard syncs.
      // The first job has no attempt.
      createJob(ctx, SYNC_1_ID);

      // The second job has one attempt.
      long job2 = createJob(ctx, SYNC_2_ID);
      createAttempt(ctx, job2, 1, createAttemptOutput(SYNC_2_STATE));

      // The third job has multiple attempts. The third attempt has the latest state.
      long job3 = createJob(ctx, SYNC_3_ID);
      JsonNode attempt31State = Jsons.deserialize("{ \"state\": { \"cursor\": 31 } }");
      createAttempt(ctx, job3, 1, createAttemptOutput(attempt31State));
      createAttempt(ctx, job3, 2, null);
      createAttempt(ctx, job3, 3, createAttemptOutput(SYNC_3_STATE));
      createAttempt(ctx, job3, 4, null);
      createAttempt(ctx, job3, 5, null);

      final Map<String, JsonNode> syncToStateMap = V0_29_21_001__Store_last_sync_state.getSyncToStateMap(jobDatabase);
      assertEquals(2, syncToStateMap.size());
      assertEquals(SYNC_2_STATE, syncToStateMap.get(SYNC_2_ID.toString()));
      assertEquals(SYNC_3_STATE, syncToStateMap.get(SYNC_3_ID.toString()));

      return null;
    });
  }

  @Test
  @Order(30)
  public void testCreateTable() throws SQLException {
    database.query(ctx -> {
      checkTable(ctx, false);
      V0_29_21_001__Store_last_sync_state.createTable(ctx);
      checkTable(ctx, true);
      return null;
    });
  }

  /**
   * Test the unique index on the sync_id column.
   */
  @Test
  @Order(40)
  public void testUniqueSyncIdIndex() throws SQLException {
    final UUID syncId = UUID.randomUUID();

    database.query(ctx -> {
      final InsertSetMoreStep<?> insertRecord = ctx.insertInto(V0_29_21_001__Store_last_sync_state.SYNC_STATE_TABLE)
          .set(V0_29_21_001__Store_last_sync_state.COLUMN_SYNC_ID, syncId)
          .set(V0_29_21_001__Store_last_sync_state.COLUMN_STATE, JSONB.valueOf("{}"));

      assertDoesNotThrow(insertRecord::execute);
      // insert the record with the same sync_id will violate the unique index
      assertThrows(org.jooq.exception.DataAccessException.class, insertRecord::execute);
      return null;
    });
  }

  @Test
  @Order(50)
  public void testCopyData() throws SQLException {
    final JsonNode sync2NewState = Jsons.deserialize("{ \"state\": { \"cursor\": 3 } }");

    final Map<String, JsonNode> syncStateMap1 = Map.of(SYNC_1_ID.toString(), SYNC_2_STATE, SYNC_2_ID.toString(), SYNC_2_STATE);
    final Map<String, JsonNode> syncStateMap2 = Map.of(SYNC_2_ID.toString(), sync2NewState);

    final OffsetDateTime timestamp = OffsetDateTime.now();

    database.query(ctx -> {
      V0_29_21_001__Store_last_sync_state.copyData(ctx, syncStateMap1, timestamp);
      checkSyncStates(ctx, syncStateMap1, timestamp);

      // call the copyData method again with different data will not affect existing records
      V0_29_21_001__Store_last_sync_state.copyData(ctx, syncStateMap2, OffsetDateTime.now());
      // the states remain the same as those in syncStateMap1
      checkSyncStates(ctx, syncStateMap1, timestamp);

      return null;
    });
  }

  /**
   * Clear the table and test the migration end-to-end.
   */
  @Test
  @Order(60)
  public void testMigration() throws Exception {
    database.query(ctx -> ctx.dropTableIfExists(V0_29_21_001__Store_last_sync_state.SYNC_STATE_TABLE).execute());

    final Configs configs = mock(Configs.class);
    when(configs.getDatabaseUser()).thenReturn(container.getUsername());
    when(configs.getDatabasePassword()).thenReturn(container.getPassword());
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());

    final var migration = new V0_29_21_001__Store_last_sync_state(configs);
    // this context is a flyway class; only the getConnection method is needed to run the migration
    final Context context = new Context() {

      @Override
      public Configuration getConfiguration() {
        return null;
      }

      @Override
      public Connection getConnection() {
        try {
          return database.getDataSource().getConnection();
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      }

    };
    migration.migrate(context);
    database.query(ctx -> {
      checkSyncStates(ctx, Map.of(SYNC_2_ID.toString(), SYNC_2_STATE, SYNC_3_ID.toString(), SYNC_3_STATE), null);
      return null;
    });
  }

  /**
   * Create a job record whose scope equals to the passed in standard sync id, and return the job id.
   */
  private static long createJob(DSLContext ctx, UUID standardSyncId) {
    final int insertCount = ctx.insertInto(JOBS_TABLE, JOB_SCOPE_FIELD)
        .values(standardSyncId.toString())
        .execute();
    assertEquals(1, insertCount);

    return ctx.select(JOB_ID_FIELD)
        .from(JOBS_TABLE)
        .where(JOB_SCOPE_FIELD.eq(standardSyncId.toString()))
        .fetchOne()
        .get(JOB_ID_FIELD);
  }

  private static void createAttempt(DSLContext ctx, long jobId, int attemptNumber, JsonNode attemptOutput) {
    final int insertCount = ctx.insertInto(ATTEMPTS_TABLE, ATTEMPT_JOB_ID_FIELD, ATTEMPT_NUMBER_FIELD, ATTEMPT_OUTPUT_FIELD)
        .values(jobId, attemptNumber, JSONB.valueOf(Jsons.serialize(attemptOutput)))
        .execute();
    assertEquals(1, insertCount);

    ctx.select(ATTEMPT_ID_FIELD)
        .from(ATTEMPTS_TABLE)
        .where(ATTEMPT_JOB_ID_FIELD.eq(jobId), ATTEMPT_NUMBER_FIELD.eq(attemptNumber))
        .fetchOne()
        .get(ATTEMPT_ID_FIELD);
  }

  /**
   * Create an JobOutput object whose output type is StandardSyncOutput.
   *
   * @param state The state object within a StandardSyncOutput.
   */
  private static JsonNode createAttemptOutput(JsonNode state) {
    final ObjectNode standardSyncOutput = OBJECT_MAPPER.createObjectNode()
        .set("state", state);
    return OBJECT_MAPPER.createObjectNode()
        .put("output_type", "sync")
        .set("sync", standardSyncOutput);
  }

  private static void checkTable(final DSLContext ctx, final boolean tableExists) {
    final List<Table<?>> tables = ctx.meta().getTables(V0_29_21_001__Store_last_sync_state.SYNC_STATE_TABLE.getName());
    assertEquals(tableExists, tables.size() > 0);

    if (!tableExists) {
      assertTrue(tables.isEmpty());
    } else {
      System.out.println(Arrays.stream(tables.get(0).fields()).map(Typed::getDataType).collect(Collectors.toSet()));
      final Set<String> actualFields = Arrays.stream(tables.get(0).fields()).map(Field::getName).collect(Collectors.toSet());
      final Set<String> expectedFields = Set.of(
          V0_29_21_001__Store_last_sync_state.COLUMN_SYNC_ID.getName(),
          V0_29_21_001__Store_last_sync_state.COLUMN_STATE.getName(),
          V0_29_21_001__Store_last_sync_state.COLUMN_CREATED_AT.getName(),
          V0_29_21_001__Store_last_sync_state.COLUMN_UPDATED_AT.getName());
      assertEquals(expectedFields, actualFields);
    }
  }

  private static void checkSyncStates(final DSLContext ctx,
                                      final Map<String, JsonNode> expectedSyncStates,
                                      @Nullable OffsetDateTime expectedTimestamp) {
    for (final Map.Entry<String, JsonNode> entry : expectedSyncStates.entrySet()) {
      final var record = ctx
          .select(V0_29_21_001__Store_last_sync_state.COLUMN_STATE,
              V0_29_21_001__Store_last_sync_state.COLUMN_CREATED_AT,
              V0_29_21_001__Store_last_sync_state.COLUMN_UPDATED_AT)
          .from(V0_29_21_001__Store_last_sync_state.SYNC_STATE_TABLE)
          .where(V0_29_21_001__Store_last_sync_state.COLUMN_SYNC_ID.eq(UUID.fromString(entry.getKey())))
          .fetchOne();
      assertEquals(entry.getValue(), Jsons.deserialize(record.value1().data()));
      if (expectedTimestamp != null) {
        assertEquals(expectedTimestamp, record.value2());
        assertEquals(expectedTimestamp, record.value3());
      }
    }
  }

}
