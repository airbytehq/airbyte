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

public class V0_35_46_001__AddMissingIndices extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_46_001__AddMissingIndices.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());

    ctx.createIndexIfNotExists("actor_workspace_id_idx").on("actor", "workspace_id").execute();
    ctx.createIndexIfNotExists("connection_operation_connection_id_idx").on("connection_operation", "connection_id").execute();
  }

}
