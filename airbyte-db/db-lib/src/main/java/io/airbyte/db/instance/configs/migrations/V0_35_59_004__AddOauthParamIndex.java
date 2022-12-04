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

public class V0_35_59_004__AddOauthParamIndex extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_59_004__AddOauthParamIndex.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    ctx.createIndexIfNotExists("actor_oauth_parameter_workspace_definition_idx").on("actor_oauth_parameter", "workspace_id", "actor_definition_id")
        .execute();
  }

}
