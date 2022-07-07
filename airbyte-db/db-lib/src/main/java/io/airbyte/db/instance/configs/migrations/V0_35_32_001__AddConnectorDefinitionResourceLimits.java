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

public class V0_35_32_001__AddConnectorDefinitionResourceLimits extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_32_001__AddConnectorDefinitionResourceLimits.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    addResourceReqsToActorDefs(ctx);
  }

  public static void addResourceReqsToActorDefs(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field("resource_requirements", SQLDataType.JSONB.nullable(true)))
        .execute();
  }

}
