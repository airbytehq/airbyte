/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Set;
import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_40_17_001__AddAuditLog extends BaseJavaMigration {

  private static final UUID PLACEHOLDER_CREATED_BY = UUID.fromString("00000000-0000-0000-0000-000000000000");
  private static final Field<UUID> DEFAULT_CREATED_BY_COLUMN =
      DSL.field("updated_by", SQLDataType.UUID.nullable(false).defaultValue(PLACEHOLDER_CREATED_BY));

  private static final Set<String> TABLE_TO_TRACK = Set.of(
      "actor_definition",
      "actor",
      "actor_oauth_parameter",
      "connection",
      "connection_operation",
      "operation",
      "stream_reset",
      "workspace",
      "workspace_service_account"
  // "state" todo (cgardens) should we do this one too?
  );

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_40_17_001__AddAuditLog.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());

    // set up functions
    createConfigEventTableAndFunctions(ctx);

    // add created_by to tables
    for (final String tableName : TABLE_TO_TRACK) {
      addCreatedByToTable(ctx, tableName);
      trackUpdatesToTable(ctx, tableName);
    }
  }

  private static void createConfigEventTableAndFunctions(final DSLContext ctx) throws IOException {
    ctx.execute(MoreResources.readResource("sql_functions_and_triggers/config_events.sql"));
    LOGGER.info("created config_event table and config event functions and triggers");
  }

  private static void addCreatedByToTable(final DSLContext ctx, final String tableName) {
    ctx.alterTable(tableName).addColumn(DEFAULT_CREATED_BY_COLUMN).execute();
    LOGGER.info(String.format("created updated_by column for %s table.", tableName));
  }

  private static void trackUpdatesToTable(final DSLContext ctx, final String tableName) {
    ctx.execute(String.format("SELECT create_config_event_trigger('%s');", tableName));
    LOGGER.info(String.format("added event trigger for %s table.", tableName));
  }

}
