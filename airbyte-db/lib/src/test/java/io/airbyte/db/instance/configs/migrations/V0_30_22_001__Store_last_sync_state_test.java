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
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
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
import java.util.concurrent.TimeUnit;
import javax.annotation.Nullable;
import org.flywaydb.core.api.configuration.Configuration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Table;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.Timeout;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class V0_30_22_001__Store_last_sync_state_test extends AbstractConfigsDatabaseTest {

  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();
  private static final OffsetDateTime TIMESTAMP = OffsetDateTime.now();

  private static final Table<?> JOBS_TABLE = table("jobs");
  private static final Field<Long> JOB_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<String> JOB_SCOPE_FIELD = field("scope", SQLDataType.VARCHAR);
  private static final Field<OffsetDateTime> JOB_CREATED_AT_FIELD = field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE);

  private static final Table<?> ATTEMPTS_TABLE = table("attempts");
  private static final Field<Long> ATTEMPT_ID_FIELD = field("id", SQLDataType.BIGINT);
  private static final Field<Long> ATTEMPT_JOB_ID_FIELD = field("job_id", SQLDataType.BIGINT);
  private static final Field<Integer> ATTEMPT_NUMBER_FIELD = field("attempt_number", SQLDataType.INTEGER);
  private static final Field<JSONB> ATTEMPT_OUTPUT_FIELD = field("output", SQLDataType.JSONB);
  private static final Field<OffsetDateTime> ATTEMPT_CREATED_AT_FIELD = field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE);

  private static final UUID CONNECTION_1_ID = UUID.randomUUID();
  private static final UUID CONNECTION_2_ID = UUID.randomUUID();
  private static final UUID CONNECTION_3_ID = UUID.randomUUID();

  private static final State CONNECTION_2_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 2222 } }", State.class);
  private static final State CONNECTION_3_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": 3333 } }", State.class);
  private static final State CONNECTION_OLD_STATE = Jsons.deserialize("{ \"state\": { \"cursor\": -1 } }", State.class);

  private static final StandardSyncState STD_CONNECTION_STATE_2 = getStandardSyncState(CONNECTION_2_ID, CONNECTION_2_STATE);
  private static final StandardSyncState STD_CONNECTION_STATE_3 = getStandardSyncState(CONNECTION_3_ID, CONNECTION_3_STATE);
  private static final Set<StandardSyncState> STD_CONNECTION_STATES = Set.of(STD_CONNECTION_STATE_2, STD_CONNECTION_STATE_3);

  private Database jobDatabase;

  @BeforeEach
  @Timeout(value = 2,
           unit = TimeUnit.MINUTES)
  public void setupJobDatabase() throws Exception {
    jobDatabase = new JobsDatabaseInstance(dslContext).getAndInitialize();
  }

  @Test
  @Order(10)
  public void testGetJobsDatabase() {
    assertTrue(V0_30_22_001__Store_last_sync_state.getJobsDatabase("", "", "").isEmpty());

    // when there is database environment variable, return the database
    final Configs configs = mock(Configs.class);
    when(configs.getDatabaseUser()).thenReturn(container.getUsername());
    when(configs.getDatabasePassword()).thenReturn(container.getPassword());
    when(configs.getDatabaseUrl()).thenReturn(container.getJdbcUrl());

    assertTrue(V0_30_22_001__Store_last_sync_state
        .getJobsDatabase(configs.getDatabaseUser(), configs.getDatabasePassword(), configs.getDatabaseUrl()).isPresent());
  }

  @Test
  @Order(20)
  public void testGetStandardSyncStates() throws Exception {
    jobDatabase.query(ctx -> {
      // Connection 1 has 1 job, no attempt.
      // This is to test that connection without no state is not returned.
      createJob(ctx, CONNECTION_1_ID, 30);

      // Connection 2 has two jobs, each has one attempt.
      // This is to test that only the state from the latest job is returned.
      final long job21 = createJob(ctx, CONNECTION_2_ID, 10);
      final long job22 = createJob(ctx, CONNECTION_2_ID, 20);
      assertNotEquals(job21, job22);
      createAttempt(ctx, job21, 1, createAttemptOutput(CONNECTION_OLD_STATE), 11);
      createAttempt(ctx, job22, 1, createAttemptOutput(CONNECTION_2_STATE), 21);

      // Connection 3 has two jobs.
      // The first job has multiple attempts. Its third attempt has the latest state.
      // The second job has two attempts with no state.
      // This is to test that only the state from the latest attempt is returned.
      final long job31 = createJob(ctx, CONNECTION_3_ID, 5);
      final long job32 = createJob(ctx, CONNECTION_3_ID, 15);
      assertNotEquals(job31, job32);
      createAttempt(ctx, job31, 1, createAttemptOutput(CONNECTION_OLD_STATE), 6);
      createAttempt(ctx, job31, 2, null, 7);
      createAttempt(ctx, job31, 3, createAttemptOutput(CONNECTION_3_STATE), 8);
      createAttempt(ctx, job31, 4, null, 9);
      createAttempt(ctx, job31, 5, null, 10);
      createAttempt(ctx, job32, 1, null, 20);
      createAttempt(ctx, job32, 2, null, 25);

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

    final OffsetDateTime timestampWithFullPrecision = OffsetDateTime.now();
    /*
     * The AWS CI machines get a higher precision value here (2021-12-07T19:56:28.967213187Z) vs what is
     * retrievable on Postgres or on my local machine (2021-12-07T19:56:28.967213Z). Truncating the
     * value to match.
     */
    final OffsetDateTime timestamp = timestampWithFullPrecision.withNano(1000 * (timestampWithFullPrecision.getNano() / 1000));

    jobDatabase.query(ctx -> {
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
    jobDatabase.query(ctx -> ctx.deleteFrom(TABLE_AIRBYTE_CONFIGS)
        .where(COLUMN_CONFIG_TYPE.eq(ConfigSchema.STANDARD_SYNC_STATE.name()))
        .execute());

    final var migration = new V0_30_22_001__Store_last_sync_state(container.getUsername(), container.getPassword(), container.getJdbcUrl());
    // this context is a flyway class; only the getConnection method is needed to run the migration
    final Context context = new Context() {

      @Override
      public Configuration getConfiguration() {
        return null;
      }

      @Override
      public Connection getConnection() {
        try {
          return dataSource.getConnection();
        } catch (final SQLException e) {
          throw new RuntimeException(e);
        }
      }

    };
    migration.migrate(context);
    jobDatabase.query(ctx -> {
      checkSyncStates(ctx, STD_CONNECTION_STATES, null);
      return null;
    });
  }

  /**
   * Create a job record whose scope equals to the passed in connection id, and return the job id.
   *
   * @param creationOffset Set the creation timestamp to {@code TIMESTAMP} + this passed in offset.
   */
  private static long createJob(final DSLContext ctx, final UUID connectionId, final long creationOffset) {
    final int insertCount = ctx.insertInto(JOBS_TABLE)
        .set(JOB_SCOPE_FIELD, connectionId.toString())
        .set(JOB_CREATED_AT_FIELD, TIMESTAMP.plusDays(creationOffset))
        .execute();
    assertEquals(1, insertCount);

    return ctx.select(JOB_ID_FIELD)
        .from(JOBS_TABLE)
        .where(JOB_SCOPE_FIELD.eq(connectionId.toString()))
        .orderBy(JOB_CREATED_AT_FIELD.desc())
        .limit(1)
        .fetchOne()
        .get(JOB_ID_FIELD);
  }

  /**
   * @param creationOffset Set the creation timestamp to {@code TIMESTAMP} + this passed in offset.
   */
  private static void createAttempt(final DSLContext ctx,
                                    final long jobId,
                                    final int attemptNumber,
                                    final JobOutput attemptOutput,
                                    final long creationOffset) {
    final int insertCount = ctx.insertInto(ATTEMPTS_TABLE)
        .set(ATTEMPT_JOB_ID_FIELD, jobId)
        .set(ATTEMPT_NUMBER_FIELD, attemptNumber)
        .set(ATTEMPT_OUTPUT_FIELD, JSONB.valueOf(Jsons.serialize(attemptOutput)))
        .set(ATTEMPT_CREATED_AT_FIELD, TIMESTAMP.plusDays(creationOffset))
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
