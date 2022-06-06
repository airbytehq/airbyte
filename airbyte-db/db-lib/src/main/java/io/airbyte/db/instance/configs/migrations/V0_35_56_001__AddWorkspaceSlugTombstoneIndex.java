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

public class V0_35_56_001__AddWorkspaceSlugTombstoneIndex extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(
      V0_35_56_001__AddWorkspaceSlugTombstoneIndex.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    ctx.createIndexIfNotExists("workspace_slug_idx").on("workspace", "slug");
    ctx.createIndexIfNotExists("workspace_tombstone_idx").on("workspace", "tombstone");
  }

}
