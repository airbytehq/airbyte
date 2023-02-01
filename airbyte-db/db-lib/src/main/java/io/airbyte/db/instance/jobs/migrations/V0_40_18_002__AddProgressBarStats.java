/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;
import static org.jooq.impl.DSL.unique;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The estimated columns contains the overall estimated records and bytes for an attempt.
 * <p>
 * The new stream_stats table contains the estimated and emitted records/bytes for an attempt at the
 * per-stream level. This lets us track per-stream stats as an attempt is in progress.
 */
public class V0_40_18_002__AddProgressBarStats extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_18_002__AddProgressBarStats.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    try (final DSLContext ctx = DSL.using(context.getConnection())) {
      addEstimatedColumnsToSyncStats(ctx);
      addStreamStatsTable(ctx);
    }
  }

  private static void addEstimatedColumnsToSyncStats(final DSLContext ctx) {
    ctx.alterTable("sync_stats")
        .add(
            field("estimated_records", SQLDataType.BIGINT.nullable(true)),
            field("estimated_bytes", SQLDataType.BIGINT.nullable(true)))
        .execute();
  }

  private static void addStreamStatsTable(final DSLContext ctx) {
    // Metadata Columns
    final Field<UUID> id = field("id", SQLDataType.UUID.nullable(false));
    final Field<Integer> attemptId = field("attempt_id", SQLDataType.INTEGER.nullable(false));
    final Field<String> streamNamespace = field("stream_namespace", SQLDataType.VARCHAR.nullable(false));
    final Field<String> streamName = field("stream_name", SQLDataType.VARCHAR.nullable(false));

    // Stats Columns
    final Field<Long> recordsEmitted = field("records_emitted", SQLDataType.BIGINT.nullable(true));
    final Field<Long> bytesEmitted = field("bytes_emitted", SQLDataType.BIGINT.nullable(true));
    final Field<Long> estimatedRecords = field("estimated_records", SQLDataType.BIGINT.nullable(true));
    final Field<Long> estimatedBytes = field("estimated_bytes", SQLDataType.BIGINT.nullable(true));

    // Time Columns
    final Field<OffsetDateTime> createdAt =
        field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("stream_stats")
        .columns(
            id, attemptId, streamNamespace, streamName, recordsEmitted, bytesEmitted, estimatedRecords, estimatedBytes, createdAt, updatedAt)
        .constraints(
            primaryKey(id),
            foreignKey(attemptId).references("attempts", "id").onDeleteCascade(),
            // Prevent duplicate stat records of the same stream and attempt.
            unique("attempt_id", "stream_name"))
        .execute();

    // Create an index on attempt_id, since all read queries on this table as of this migration will be
    // WHERE clauses on the attempt id.
    ctx.createIndex("index").on("stream_stats", "attempt_id").execute();

  }

}
