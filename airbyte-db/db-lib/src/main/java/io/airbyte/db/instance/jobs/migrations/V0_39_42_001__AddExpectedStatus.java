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

public class V0_39_42_001__AddExpectedStatus extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_39_42_001__AddExpectedStatus.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  public static void migrate(final DSLContext ctx) {
    addExpectedStatusToJobsTable(ctx);
  }

  public static void addExpectedStatusToJobsTable(final DSLContext ctx) {
    ctx.alterTable("jobs")
        .addColumnIfNotExists(DSL.field("expected_status", SQLDataType.VARCHAR(255).nullable(true)))
        .execute();
  }

}
