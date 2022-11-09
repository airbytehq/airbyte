/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * These new columns are required for progress bars.
 * <p>
 * - the estimated columns will contain the overall estimated records and bytes for the sync.
 * <p>
 * - the StreamStats column will contain a list of {@link io.airbyte.config.StreamSyncStats}. This
 * is the estimated and currently emitted stats for each stream. As streams are varied, a JSON blob
 * is simpler to manage for now. The alternative is a stream stats table with a foreign key to an
 * attempt. It is not clear we will benefit from a structured relational database at this point.
 */
public class V0_40_18_001__AddEstimatedAndStreamStatsColumnSyncStats extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_18_001__AddEstimatedAndStreamStatsColumnSyncStats.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    ctx.alterTable("sync_stats")
        .add(
            DSL.field("estimated_records", SQLDataType.BIGINT.nullable(true)),
            DSL.field("estimated_bytes", SQLDataType.BIGINT.nullable(true)),
            DSL.field("stream_stats", SQLDataType.JSONB.nullable(true)))
        .execute();
  }

}
