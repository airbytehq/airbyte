/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_62_001__AddJobIndices extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_62_001__AddJobIndices.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    try (final DSLContext ctx = DSL.using(context.getConnection())) {
      ctx.createIndexIfNotExists("jobs_config_type_idx").on("jobs", "config_type").execute();
      ctx.createIndexIfNotExists("jobs_scope_idx").on("jobs", "scope").execute();
    }
  }

}
