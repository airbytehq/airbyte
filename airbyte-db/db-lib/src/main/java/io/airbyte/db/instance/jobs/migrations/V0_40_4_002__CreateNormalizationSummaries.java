/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO: update migration description in the class name
public class V0_40_4_002__CreateNormalizationSummaries extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_4_002__CreateNormalizationSummaries.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    createNormalizationSummariesTable(ctx);
  }

  private void createNormalizationSummariesTable(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<Long> attemptId = DSL.field("attempt_id", SQLDataType.BIGINT.nullable(false));
    final Field<OffsetDateTime> startTime = DSL.field("start_time", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(true));
    final Field<OffsetDateTime> endTime = DSL.field("end_time", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(true));
    final Field<JSONB> failures = DSL.field("failures", SQLDataType.JSONB.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("normalization_summaries")
        .columns(id, attemptId, startTime, endTime, failures, createdAt, updatedAt)
        .constraints(primaryKey(id), foreignKey(attemptId).references("attempts", "id").onDeleteCascade())
        .execute();

    ctx.createIndex("normalization_summary_attempt_id_idx").on("normalization_summaries", "attempt_id").execute();

  }

}
