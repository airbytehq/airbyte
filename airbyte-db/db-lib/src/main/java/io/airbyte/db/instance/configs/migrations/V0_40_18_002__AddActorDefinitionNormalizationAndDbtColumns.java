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

public class V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumns extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_18_002__AddActorDefinitionNormalizationAndDbtColumns.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());
    final DSLContext ctx = DSL.using(context.getConnection());
    addNormalizationRepositoryColumn(ctx);
    addNormalizationTagColumn(ctx);
    addSupportsDbtColumn(ctx);
  }

  static void addNormalizationRepositoryColumn(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field(
            "normalization_repository",
            SQLDataType.VARCHAR(255).nullable(true)))
        .execute();
  }

  static void addNormalizationTagColumn(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field(
            "normalization_tag",
            SQLDataType.VARCHAR(255).nullable(true)))
        .execute();
  }

  static void addSupportsDbtColumn(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field("supports_dbt",
            SQLDataType.BOOLEAN.nullable(true)))
        .execute();
  }

}
