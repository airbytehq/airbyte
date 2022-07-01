/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.Catalog;
import org.jooq.DSLContext;
import org.jooq.EnumType;
import org.jooq.Schema;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.jooq.impl.SchemaImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    createReleaseStageEnum(ctx);
    addReleaseStageColumn(ctx);
    addReleaseDateColumn(ctx);
  }

  public static void createReleaseStageEnum(final DSLContext ctx) {
    ctx.createType("release_stage").asEnum("alpha", "beta", "generally_available", "custom").execute();
  }

  public static void addReleaseStageColumn(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field("release_stage", SQLDataType.VARCHAR.asEnumDataType(ReleaseStage.class).nullable(true)))
        .execute();
  }

  public static void addReleaseDateColumn(final DSLContext ctx) {
    ctx.alterTable("actor_definition")
        .addColumnIfNotExists(DSL.field("release_date", SQLDataType.DATE.nullable(true)))
        .execute();
  }

  public enum ReleaseStage implements EnumType {

    alpha("alpha"),
    beta("beta"),
    generally_available("generally_available"),
    custom("custom");

    private final String literal;

    ReleaseStage(String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);
    }

    @Override
    public String getName() {
      return "release_stage";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

}
