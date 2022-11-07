/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import com.google.common.annotations.VisibleForTesting;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_3_002__RemoveActorForeignKeyFromOauthParamsTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_3_002__RemoveActorForeignKeyFromOauthParamsTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());
    final DSLContext ctx = DSL.using(context.getConnection());
    removeActorDefinitionForeignKey(ctx);
  }

  @VisibleForTesting
  static void removeActorDefinitionForeignKey(final DSLContext ctx) {
    ctx.alterTable("actor_oauth_parameter").dropForeignKey("actor_oauth_parameter_actor_definition_id_fkey").execute();
  }

}
