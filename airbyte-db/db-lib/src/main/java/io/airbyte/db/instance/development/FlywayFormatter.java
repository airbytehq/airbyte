/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.development;

import static org.jooq.impl.DSL.field;

import io.airbyte.db.instance.DatabaseMigrator;
import java.sql.Date;
import java.util.List;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateOutput;
import org.flywaydb.core.api.output.MigrateResult;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record4;
import org.jooq.Record5;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDSLContext;
import org.jooq.impl.SQLDataType;

/**
 * This class formats the Flyway outputs so that it is easier to inspect them and debug the
 * migration.
 */
public class FlywayFormatter {

  private static final DSLContext CTX = new DefaultDSLContext(SQLDialect.DEFAULT);

  /**
   * Format the {@link DatabaseMigrator#list} output.
   */
  static String formatMigrationInfoList(final List<MigrationInfo> migrationInfoList) {
    final Field<String> type = field("Type", SQLDataType.VARCHAR);
    final Field<String> version = field("Version", SQLDataType.VARCHAR);
    final Field<String> description = field("Description", SQLDataType.VARCHAR);
    final Field<String> state = field("State", SQLDataType.VARCHAR);
    final Field<Date> migratedAt = field("MigratedAt", SQLDataType.DATE);
    final Result<Record5<String, String, String, String, Date>> result = CTX.newResult(type, version, description, state, migratedAt);
    migrationInfoList.forEach(info -> result.add(CTX.newRecord(type, version, description, state, migratedAt).values(
        info.getType().name(),
        info.getVersion().toString(),
        info.getDescription(),
        info.getState().getDisplayName(),
        info.getInstalledOn() == null ? null : new Date(info.getInstalledOn().getTime()))));
    return result.format();
  }

  static String formatMigrationOutputList(final List<MigrateOutput> migrationOutputList) {
    final Field<String> type = field("Type", SQLDataType.VARCHAR);
    final Field<String> version = field("Version", SQLDataType.VARCHAR);
    final Field<String> description = field("Description", SQLDataType.VARCHAR);
    final Field<String> script = field("Script", SQLDataType.VARCHAR);
    final Result<Record4<String, String, String, String>> result = CTX.newResult(type, version, description, script);
    migrationOutputList.forEach(output -> result.add(CTX.newRecord(type, version, description, script).values(
        String.format("%s %s", output.type, output.category),
        output.version,
        output.description,
        output.filepath)));
    return result.format();
  }

  /**
   * Format the {@link DatabaseMigrator#migrate} output.
   */
  static String formatMigrationResult(final MigrateResult result) {
    return String.format("Version: %s -> %s\n", result.initialSchemaVersion, result.targetSchemaVersion)
        + String.format("Migrations executed: %s\n", result.migrationsExecuted)
        + formatMigrationOutputList(result.migrations);
  }

}
