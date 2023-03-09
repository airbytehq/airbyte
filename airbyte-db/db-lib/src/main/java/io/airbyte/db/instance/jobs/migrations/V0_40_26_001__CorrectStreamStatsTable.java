/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import static org.jooq.impl.DSL.constraint;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_26_001__CorrectStreamStatsTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_26_001__CorrectStreamStatsTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    try (final DSLContext ctx = DSL.using(context.getConnection())) {
      // This actually needs to be bigint to match the id column on the attempts table.
      String streamStats = "stream_stats";
      ctx.alterTable(streamStats).alter("attempt_id").set(SQLDataType.BIGINT.nullable(false)).execute();
      // Not all streams provide a namespace.
      ctx.alterTable(streamStats).alter("stream_namespace").set(SQLDataType.VARCHAR.nullable(true)).execute();

      // The constraint should also take into account the stream namespace. Drop the constraint and
      // recreate it.
      ctx.alterTable(streamStats).dropUnique("stream_stats_attempt_id_stream_name_key").execute();
      ctx.alterTable(streamStats).add(constraint("uniq_stream_attempt").unique("attempt_id", "stream_name", "stream_namespace")).execute();
    }
  }

}
