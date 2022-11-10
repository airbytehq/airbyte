/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.SQLDialect;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Copy the latest job state for each standard sync to the config database.
 */
public class V0_30_22_001__Store_last_sync_state extends BaseJavaMigration {

  private static final String MIGRATION_NAME = "Configs db migration 0.30.22.001";
  private static final Logger LOGGER = LoggerFactory.getLogger(V0_30_22_001__Store_last_sync_state.class);

  // airbyte configs table
  // (we cannot use the jooq generated code here to avoid circular dependency)
  static final Table<?> TABLE_AIRBYTE_CONFIGS = DSL.table("airbyte_configs");
  static final Field<String> COLUMN_CONFIG_TYPE = DSL.field("config_type", SQLDataType.VARCHAR(60).nullable(false));
  static final Field<String> COLUMN_CONFIG_ID = DSL.field("config_id", SQLDataType.VARCHAR(36).nullable(false));
  static final Field<JSONB> COLUMN_CONFIG_BLOB = DSL.field("config_blob", SQLDataType.JSONB.nullable(false));
  static final Field<OffsetDateTime> COLUMN_CREATED_AT = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE);
  static final Field<OffsetDateTime> COLUMN_UPDATED_AT = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());
    final DSLContext ctx = DSL.using(context.getConnection());

    final Optional<Database> jobsDatabase = getJobsDatabase(context.getConfiguration().getUser(),
        context.getConfiguration().getPassword(), context.getConfiguration().getUrl());
    if (jobsDatabase.isPresent()) {
      copyData(ctx, getStandardSyncStates(jobsDatabase.get()), OffsetDateTime.now());
    }
  }

  @VisibleForTesting
  static void copyData(final DSLContext ctx, final Set<StandardSyncState> standardSyncStates, final OffsetDateTime timestamp) {
    LOGGER.info("[{}] Number of connection states to copy: {}", MIGRATION_NAME, standardSyncStates.size());

    for (final StandardSyncState standardSyncState : standardSyncStates) {
      ctx.insertInto(TABLE_AIRBYTE_CONFIGS)
          .set(COLUMN_CONFIG_TYPE, ConfigSchema.STANDARD_SYNC_STATE.name())
          .set(COLUMN_CONFIG_ID, standardSyncState.getConnectionId().toString())
          .set(COLUMN_CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(standardSyncState)))
          .set(COLUMN_CREATED_AT, timestamp)
          .set(COLUMN_UPDATED_AT, timestamp)
          // This migration is idempotent. If the record for a sync_id already exists,
          // it means that the migration has already been run before. Abort insertion.
          .onDuplicateKeyIgnore()
          .execute();
    }
  }

  /**
   * This migration requires a connection to the job database, which may be a separate database from
   * the config database. However, the job database only exists in production, not in development or
   * test. We use the job database environment variables to determine how to connect to the job
   * database. This approach is not 100% reliable. However, it is better than doing half of the
   * migration here (creating the table), and the rest of the work during server start up (copying the
   * data from the job database).
   */
  @VisibleForTesting
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  static Optional<Database> getJobsDatabase(final String databaseUser, final String databasePassword, final String databaseUrl) {
    try {
      if (databaseUrl == null || "".equals(databaseUrl.trim())) {
        throw new IllegalArgumentException("The databaseUrl cannot be empty.");
      }
      // If the environment variables exist, it means the migration is run in production.
      // Connect to the official job database.
      final DSLContext dslContext =
          DSLContextFactory.create(databaseUser, databasePassword, DatabaseDriver.POSTGRESQL.getDriverClassName(), databaseUrl, SQLDialect.POSTGRES);
      final Database jobsDatabase = new Database(dslContext);
      LOGGER.info("[{}] Connected to jobs database: {}", MIGRATION_NAME, databaseUrl);
      return Optional.of(jobsDatabase);
    } catch (final IllegalArgumentException e) {
      // If the environment variables do not exist, it means the migration is run in development.
      LOGGER.info("[{}] This is the dev environment; there is no jobs database", MIGRATION_NAME);
      return Optional.empty();
    }
  }

  /**
   * @return a set of StandardSyncStates from the latest attempt for each connection.
   */
  @VisibleForTesting
  static Set<StandardSyncState> getStandardSyncStates(final Database jobsDatabase) throws SQLException {
    final Table<?> jobsTable = DSL.table("jobs");
    final Field<Long> jobId = DSL.field("jobs.id", SQLDataType.BIGINT);
    final Field<String> connectionId = DSL.field("jobs.scope", SQLDataType.VARCHAR);

    final Table<?> attemptsTable = DSL.table("attempts");
    final Field<Long> attemptJobId = DSL.field("attempts.job_id", SQLDataType.BIGINT);
    final Field<OffsetDateTime> attemptCreatedAt = DSL.field("attempts.created_at", SQLDataType.TIMESTAMPWITHTIMEZONE);

    // output schema: JobOutput.yaml
    // sync schema: StandardSyncOutput.yaml
    // state schema: State.yaml, e.g. { "state": { "cursor": 1000 } }
    final Field<JSONB> attemptState = DSL.field("attempts.output -> 'sync' -> 'state'", SQLDataType.JSONB);

    return jobsDatabase.query(ctx -> ctx
        .select(connectionId, attemptState)
        .distinctOn(connectionId)
        .from(attemptsTable)
        .innerJoin(jobsTable)
        .on(jobId.eq(attemptJobId))
        .where(attemptState.isNotNull())
        // this query assumes that an attempt with larger created_at field is always a newer attempt
        .orderBy(connectionId, attemptCreatedAt.desc())
        .fetch()
        .stream()
        .map(r -> getStandardSyncState(UUID.fromString(r.value1()), Jsons.deserialize(r.value2().data(), State.class))))
        .collect(Collectors.toSet());
  }

  @VisibleForTesting
  static StandardSyncState getStandardSyncState(final UUID connectionId, final State state) {
    return new StandardSyncState().withConnectionId(connectionId).withState(state);
  }

}
