/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO: update migration description in the class name
public class V0_40_12_001__AddWebhookOperationColumns extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_12_001__AddWebhookOperationColumns.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    addWebhookOperationConfigColumn(ctx);
    addWebhookOperationType(ctx);
    addWebhookConfigColumnsToWorkspaceTable(ctx);
  }

  private void addWebhookConfigColumnsToWorkspaceTable(final DSLContext ctx) {
    ctx.alterTable("workspace")
        .addColumnIfNotExists(DSL.field(
            "webhook_operation_configs",
            SQLDataType.JSONB.nullable(true)))
        .execute();
  }

  private void addWebhookOperationType(final DSLContext ctx) {
    ctx.alterType("operator_type").addValue("webhook").execute();
  }

  private void addWebhookOperationConfigColumn(final DSLContext ctx) {
    ctx.alterTable("operation").addColumnIfNotExists(DSL.field("operator_webhook",
        SQLDataType.JSONB.nullable(true))).execute();
  }

}
