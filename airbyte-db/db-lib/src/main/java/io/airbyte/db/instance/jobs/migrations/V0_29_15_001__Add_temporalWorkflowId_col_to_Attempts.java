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

public class V0_29_15_001__Add_temporalWorkflowId_col_to_Attempts extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_29_15_001__Add_temporalWorkflowId_col_to_Attempts.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    ctx.alterTable("attempts")
        .addColumnIfNotExists(DSL.field("temporal_workflow_id", SQLDataType.VARCHAR(256).nullable(true)))
        .execute();
  }

}
