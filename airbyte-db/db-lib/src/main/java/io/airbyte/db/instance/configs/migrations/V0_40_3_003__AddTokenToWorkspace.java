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

public class V0_40_3_003__AddTokenToWorkspace extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_3_003__AddTokenToWorkspace.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    addTokenColumn(ctx);
  }

  public static void addTokenColumn(final DSLContext ctx) {
    ctx.alterTable("workspace")
        .addColumnIfNotExists(DSL.field("token", SQLDataType.VARCHAR(32).nullable(true)))
        .execute();
  }

}
