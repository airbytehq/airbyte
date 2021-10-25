/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record2;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Create a new table to store the latest job state for each standard sync.
 * <li>Column sync_id: the connectionId in StandardSync</><li>Column state: a json node representing
 * a State object</li>
 */
public class V0_30_22_001__Store_last_sync_state extends BaseJavaMigration {

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final String MIGRATION_NAME = "Configs db migration 0.30.22.001";
  private static final Logger LOGGER = LoggerFactory.getLogger(V0_30_22_001__Store_last_sync_state.class);

  // airbyte configs table
  // (we cannot use the jooq generated code here to avoid circular dependency)
  static final String STANDARD_SYNC_STATE = "STANDARD_SYNC_STATE";
  static final Table<?> TABLE_AIRBYTE_CONFIGS = DSL.table("airbyte_configs");
  static final Field<String> COLUMN_CONFIG_TYPE = DSL.field("config_type", SQLDataType.VARCHAR(60).nullable(false));
  static final Field<String> COLUMN_CONFIG_ID = DSL.field("config_id", SQLDataType.VARCHAR(36).nullable(false));
  static final Field<JSONB> COLUMN_CONFIG_BLOB = DSL.field("config_blob", SQLDataType.JSONB.nullable(false));
  static final Field<OffsetDateTime> COLUMN_CREATED_AT = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE);
  static final Field<OffsetDateTime> COLUMN_UPDATED_AT = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE);

  private final Configs configs;

  public V0_30_22_001__Store_last_sync_state() {
    this.configs = new EnvConfigs();
  }

  @VisibleForTesting
  V0_30_22_001__Store_last_sync_state(final Configs configs) {
    this.configs = configs;
  }

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());
    final DSLContext ctx = DSL.using(context.getConnection());

    final Optional<Database> jobsDatabase = getJobsDatabase(configs);
    if (jobsDatabase.isPresent()) {
      copyData(ctx, getStandardSyncStates(jobsDatabase.get()), OffsetDateTime.now());
    }
  }

  @VisibleForTesting
  static void copyData(final DSLContext ctx, final Map<String, JsonNode> syncToStateMap, final OffsetDateTime timestamp) {
    for (final Map.Entry<String, JsonNode> entry : syncToStateMap.entrySet()) {
      ctx.insertInto(TABLE_AIRBYTE_CONFIGS)
          .set(COLUMN_CONFIG_TYPE, STANDARD_SYNC_STATE)
          .set(COLUMN_CONFIG_ID, UUID.fromString(entry.getKey()).toString())
          .set(COLUMN_CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(entry.getValue())))
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
  static Optional<Database> getJobsDatabase(final Configs configs) {
    try {
      // If the environment variables exist, it means the migration is run in production.
      // Connect to the official job database.
      final Database jobsDatabase = new JobsDatabaseInstance(
          configs.getDatabaseUser(),
          configs.getDatabasePassword(),
          configs.getDatabaseUrl())
              .getInitialized();
      LOGGER.info("[{}] Connected to jobs database: {}", MIGRATION_NAME, configs.getDatabaseUrl());
      return Optional.of(jobsDatabase);
    } catch (final IllegalArgumentException e) {
      // If the environment variables do not exist, it means the migration is run in development.
      // Connect to a mock job database, because we don't need to copy any data in test.
      LOGGER.info("[{}] This is the dev environment; there is no jobs database", MIGRATION_NAME);
      return Optional.empty();
    } catch (final IOException e) {
      throw new RuntimeException("Cannot connect to jobs database", e);
    }
  }

  /**
   * @return a map from connection id (UUID) to connection state (StandardSyncState).
   */
  @VisibleForTesting
  static Map<String, JsonNode> getStandardSyncStates(final Database jobsDatabase) throws SQLException {
    final Table<?> jobsTable = DSL.table("jobs");
    final Field<Long> jobIdField = DSL.field("jobs.id", SQLDataType.BIGINT);
    final Field<String> syncIdField = DSL.field("jobs.scope", SQLDataType.VARCHAR);

    final Table<?> attemptsTable = DSL.table("attempts");
    final Field<Long> attemptJobIdField = DSL.field("attempts.job_id", SQLDataType.BIGINT);
    final Field<Integer> attemptNumberField = DSL.field("attempts.attempt_number", SQLDataType.INTEGER);

    // output schema: JobOutput.yaml
    // sync schema: StandardSyncOutput.yaml
    // state schema: State.yaml, e.g. { "state": { "cursor": 1000 } }
    final Field<JSONB> attemptStateField = DSL.field("attempts.output -> 'sync' -> 'state'", SQLDataType.JSONB);

    return jobsDatabase.query(ctx -> ctx
        .select(syncIdField, attemptStateField)
        .from(attemptsTable)
        .innerJoin(jobsTable)
        .on(jobIdField.eq(attemptJobIdField))
        .where(DSL.row(attemptJobIdField, attemptNumberField).in(
            // for each job id, find the last attempt with a state
            DSL.select(attemptJobIdField, DSL.max(attemptNumberField))
                .from(attemptsTable)
                .where(attemptStateField.isNotNull())
                .groupBy(attemptJobIdField)))
        .fetch()
        .stream()
        .collect(Collectors.toMap(
            Record2::value1,
            r -> getStandardSyncState(r.value1(), Jsons.deserialize(r.value2().data())))));
  }

  @VisibleForTesting
  static JsonNode getStandardSyncState(final String connectionId, final JsonNode state) {
    return MAPPER.createObjectNode()
        .put("connectionId", connectionId)
        .set("state", state);
  }

}
