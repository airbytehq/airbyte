/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_18_003__AddIndexToConnectionStatus extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_18_003__AddIndexToConnectionStatus.class);
  private static final String CONNECTION_TABLE = "connection";

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    try (final DSLContext ctx = DSL.using(context.getConnection())) {
      ctx.createIndexIfNotExists("connection_status_idx").on(CONNECTION_TABLE, "status").execute();
    }
  }

}
