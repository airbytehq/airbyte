/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import java.util.Arrays;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.EnumType;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_11_002__AddSchemaChangeColumnsToConnections extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_11_002__AddSchemaChangeColumnsToConnections.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());

    addNonBreakingChangePreferenceEnumTypes(ctx);

    addNotifySchemaChanges(ctx);
    addNonBreakingChangePreference(ctx);
    addBreakingChange(ctx);
  }

  private static void addNonBreakingChangePreferenceEnumTypes(final DSLContext ctx) {
    ctx.createType(NonBreakingChangePreferenceType.NAME)
        .asEnum(Arrays.stream(NonBreakingChangePreferenceType.values()).map(NonBreakingChangePreferenceType::getLiteral).toList())
        .execute();
  }

  private static void addNotifySchemaChanges(final DSLContext ctx) {
    ctx.alterTable("connection")
        .addColumnIfNotExists(DSL.field(
            "notify_schema_changes",
            SQLDataType.BOOLEAN.nullable(false).defaultValue(true)))
        .execute();
  }

  private static void addNonBreakingChangePreference(final DSLContext ctx) {
    ctx.alterTable("connection")
        .addColumnIfNotExists(DSL.field(
            "non_breaking_change_preference",
            SQLDataType.VARCHAR.asEnumDataType(NonBreakingChangePreferenceType.class).nullable(false)
                .defaultValue(NonBreakingChangePreferenceType.IGNORE)))
        .execute();

  }

  private static void addBreakingChange(final DSLContext ctx) {
    ctx.alterTable("connection")
        .addColumnIfNotExists(DSL.field(
            "breaking_change",
            SQLDataType.BOOLEAN.nullable(false).defaultValue(false)))
        .execute();
  }

  public enum NonBreakingChangePreferenceType implements EnumType {

    IGNORE("ignore"),
    DISABLE("disable");

    private final String literal;
    public static final String NAME = "non_breaking_change_preference_type";

    NonBreakingChangePreferenceType(final String literal) {
      this.literal = literal;
    }

    @Override
    public String getName() {
      return NAME;
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

}
