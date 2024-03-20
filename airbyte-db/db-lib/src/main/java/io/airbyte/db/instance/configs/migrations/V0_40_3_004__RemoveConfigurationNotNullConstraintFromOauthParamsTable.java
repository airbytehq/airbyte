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

public class V0_40_3_004__RemoveConfigurationNotNullConstraintFromOauthParamsTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_3_004__RemoveConfigurationNotNullConstraintFromOauthParamsTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    removeConstraint(ctx);
  }

  public static void removeConstraint(final DSLContext ctx) {
    ctx.alterTable("actor_oauth_parameter").alterColumn("configuration").dropNotNull().execute();
  }

}
