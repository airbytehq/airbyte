/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.COLUMN_CONFIG_BLOB;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.COLUMN_CONFIG_ID;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.COLUMN_CONFIG_TYPE;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.COLUMN_CREATED_AT;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.COLUMN_UPDATED_AT;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.TABLE_AIRBYTE_CONFIGS;
import static io.airbyte.db.instance.configs.migrations.V0_30_22_001__Store_last_sync_state.getStandardSyncState;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobOutput.OutputType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.Set;
import java.util.UUID;
import javax.annotation.Nullable;
import org.flywaydb.core.api.configuration.Configuration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Table;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class V0_30_22_001__Store_last_sync_state_test extends AbstractConfigsDatabaseTest {

  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();

  private static final Table<?> JOBS_TABLE = table("jobs");
  private static final Field<Long> JOB_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<String> JOB_SCOPE_FIELD = field("scope", SQLDataType.VARCHAR);

  private static final Table<?> ATTEMPTS_TABLE = table("attempts");
  private static final Field<Long> ATTEMPT_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<Long> ATTEMPT_JOB_ID_FIELD = field("job_id", SQLDataType.BIGINT);
  private static final Field<Integer> ATTEMPT_NUMBER_FIELD = field("attempt_number", SQLDataType.INTEGER);
  private static final Field<JSONB> ATTEMPT_OUTPUT_FIELD = field("output", SQLDataType.JSONB);

  private static final UUID CONNECTION_1_ID = UUID.randomUUID();
  private static final UUID CONNECTION_2_ID = UUID.randomUUID();
  private static final UUID CONNECTION_3_ID = UUID.randomUUID();

  private static final State CONNECTION_2_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 2222 } }", State.class);
  private static final State CONNECTION_3_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 3333 } }", State.class);

  private static final StandardSyncState STD_CONNECTION_STATE_2 = getStandardSyncState(CONNECTION_2_ID, CONNECTION_2_STATE);
  private static final StandardSyncState STD_CONNECTION_STATE_3 = getStandardSyncState(CONNECTION_3_ID, CONNECTION_3_STATE);
  private static final Set<StandardSyncState> STD_CONNECTION_STATES = Set.of(STD_CONNECTION_STATE_2, STD_CONNECTION_STATE_3);

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
    assertTrue(V0_30_22_001__Store_last_sync_state.getJobsDatabase(new EnvConfigs()).isEmpty());

    // when there is database environment variable, return the database
    final Configs configs = mock(Configs.class);
    when(configs.getDatabaseUser()).thenReturn(container.getUsername());
    when(configs.getDatabasePassword()).thenReturn(container.getPassword());
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());

    assertTrue(V0_30_22_001__Store_last_sync_state.getJobsDatabase(configs).isPresent());
  }

  @Test
  @Order(20)
  public void testGetSyncToStateMap() throws Exception {
    jobDatabase.query(ctx -> {
      // Create three jobs for three standard syncs.
      // The first job has no attempt.
      createJob(ctx, CONNECTION_1_ID);

      // The second job has one attempt.
      final long job2 = createJob(ctx, CONNECTION_2_ID);
      createAttempt(ctx, job2, 1, createAttemptOutput(CONNECTION_2_STATE));

      // The third job has multiple attempts. The third attempt has the latest state.
      final long job3 = createJob(ctx, CONNECTION_3_ID);
      final State attempt31State = new State().withState(Jsons.deserialize("{\"cursor\": 31 }"));
      createAttempt(ctx, job3, 1, createAttemptOutput(attempt31State));
      createAttempt(ctx, job3, 2, null);
      createAttempt(ctx, job3, 3, createAttemptOutput(CONNECTION_3_STATE));
      createAttempt(ctx, job3, 4, null);
      createAttempt(ctx, job3, 5, null);

      assertEquals(STD_CONNECTION_STATES, V0_30_22_001__Store_last_sync_state.getStandardSyncStates(jobDatabase));

      return null;
    });
  }

  @Test
  @Order(30)
  public void testCopyData() throws SQLException {

    final Set<StandardSyncState> newConnectionStates = Collections.singleton(
        new StandardSyncState()
            .withConnectionId(CONNECTION_2_ID)
            .withState(new State().withState(Jsons.deserialize("{ \"cursor\": 3 }"))));

    final OffsetDateTime timestamp = OffsetDateTime.now();

    database.query(ctx -> {
      V0_30_22_001__Store_last_sync_state.copyData(ctx, STD_CONNECTION_STATES, timestamp);
      checkSyncStates(ctx, STD_CONNECTION_STATES, timestamp);

      // call the copyData method again with different data will not affect existing records
      V0_30_22_001__Store_last_sync_state.copyData(ctx, newConnectionStates, OffsetDateTime.now());
      // the states remain the same as those in STD_CONNECTION_STATES
      checkSyncStates(ctx, STD_CONNECTION_STATES, timestamp);

      return null;
    });
  }

  /**
   * Clear the table and test the migration end-to-end.
   */
  @Test
  @Order(40)
  public void testMigration() throws Exception {
    database.query(ctx -> ctx.deleteFrom(TABLE_AIRBYTE_CONFIGS)
        .where(COLUMN_CONFIG_TYPE.eq(ConfigSchema.STANDARD_SYNC_STATE.name()))
        .execute());

    final Configs configs = mock(Configs.class);
    when(configs.getDatabaseUser()).thenReturn(container.getUsername());
    when(configs.getDatabasePassword()).thenReturn(container.getPassword());
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());

    final var migration = new V0_30_22_001__Store_last_sync_state(configs);
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
        } catch (final SQLException e) {
          throw new RuntimeException(e);
        }
      }

    };
    migration.migrate(context);
    database.query(ctx -> {
      checkSyncStates(ctx, STD_CONNECTION_STATES, null);
      return null;
    });
  }

  /**
   * Create a job record whose scope equals to the passed in standard sync id, and return the job id.
   */
  private static long createJob(final DSLContext ctx, final UUID standardSyncId) {
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

  private static void createAttempt(final DSLContext ctx, final long jobId, final int attemptNumber, final JobOutput attemptOutput) {
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
  private static JobOutput createAttemptOutput(final State state) {
    final StandardSyncOutput standardSyncOutput = new StandardSyncOutput().withState(state);
    return new JobOutput().withOutputType(OutputType.SYNC).withSync(standardSyncOutput);
  }

  private static void checkSyncStates(final DSLContext ctx,
                                      final Set<StandardSyncState> standardSyncStates,
                                      @Nullable final OffsetDateTime expectedTimestamp) {
    for (final StandardSyncState standardSyncState : standardSyncStates) {
      final var record = ctx
          .select(COLUMN_CONFIG_BLOB,
              COLUMN_CREATED_AT,
              COLUMN_UPDATED_AT)
          .from(TABLE_AIRBYTE_CONFIGS)
          .where(COLUMN_CONFIG_ID.eq(standardSyncState.getConnectionId().toString()),
              COLUMN_CONFIG_TYPE.eq(ConfigSchema.STANDARD_SYNC_STATE.name()))
          .fetchOne();
      assertEquals(standardSyncState, Jsons.deserialize(record.value1().data(), StandardSyncState.class));
      if (expectedTimestamp != null) {
        assertEquals(expectedTimestamp, record.value2());
        assertEquals(expectedTimestamp, record.value3());
      }
    }
  }

}
