/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Set all existing actor definitions to public
// This is to ensure that any existing custom actor definitions will continue to be usable by all
// workspaces
public class V0_35_56_001__SetAllExistingActorDefinitionsToPublic extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_56_001__SetAllExistingActorDefinitionsToPublic.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    setPublic(ctx);
  }

  public static void setPublic(final DSLContext ctx) {
    ctx.update(DSL.table("actor_definition"))
        .set(DSL.field("public"), true)
        .execute();
  }

}
