/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import com.google.common.annotations.VisibleForTesting;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_5_001__Add_failureSummary_col_to_Attempts extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_5_001__Add_failureSummary_col_to_Attempts.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    addFailureSummaryColumn(ctx);
  }

  public static void addFailureSummaryColumn(final DSLContext ctx) {
    ctx.alterTable("attempts")
        .addColumnIfNotExists(DSL.field("failure_summary", SQLDataType.JSONB.nullable(true)))
        .execute();
  }

}
