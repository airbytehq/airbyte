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

public class V0_36_3_001__AddScheduleTypeToConfigsTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_36_3_001__AddScheduleTypeToConfigsTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());
    final DSLContext ctx = DSL.using(context.getConnection());
    createScheduleTypeEnum(ctx);
    addPublicColumn(ctx);
  }

  private static void createScheduleTypeEnum(final DSLContext ctx) {
    ctx.createType("schedule_type").asEnum("manual", "basic_schedule", "cron").execute();
  }

  private static void addPublicColumn(final DSLContext ctx) {
    ctx.alterTable("connection")
        .addColumnIfNotExists(DSL.field(
            "schedule_type",
            SQLDataType.VARCHAR.asEnumDataType(ScheduleType.class).nullable(true)))
        .execute();
  }

  public enum ScheduleType implements EnumType {

    manual("manual"),
    basicSchedule("basic_schedule"),
    cron("cron"),;

    private final String literal;

    ScheduleType(final String literal) {
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
      return "schedule_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

}
