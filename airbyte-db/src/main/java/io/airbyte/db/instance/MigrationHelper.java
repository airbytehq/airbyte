package io.airbyte.db.instance;

import static org.jooq.impl.DSL.field;

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
 * Helper methods that format outputs of {@link DatabaseMigrator} for debugging.
 */
public class MigrationHelper {

  private static final DSLContext CTX = new DefaultDSLContext(SQLDialect.DEFAULT);

  /**
   * Format the {@link DatabaseMigrator#info} output.
   */
  public static String format(List<MigrationInfo> migrationInfoList) {
    Field<String> type = field("Type", SQLDataType.VARCHAR);
    Field<String> version = field("Version", SQLDataType.VARCHAR);
    Field<String> description = field("Description", SQLDataType.VARCHAR);
    Field<String> state = field("State", SQLDataType.VARCHAR);
    Field<Date> migratedAt = field("MigratedAt", SQLDataType.DATE);
    Result<Record5<String, String, String, String, Date>> result = CTX.newResult(type, version, description, state, migratedAt);
    migrationInfoList.forEach(info -> result.add(CTX.newRecord(type, version, description, state, migratedAt).values(
        info.getType().name(),
        info.getVersion().toString(),
        info.getDescription(),
        info.getState().name(),
        info.getInstalledOn() == null ? null : new Date(info.getInstalledOn().getTime()))));
    return result.format();
  }

  public static String formatOutputs(List<MigrateOutput> migrationOutputList) {
    Field<String> type = field("Type", SQLDataType.VARCHAR);
    Field<String> version = field("Version", SQLDataType.VARCHAR);
    Field<String> description = field("Description", SQLDataType.VARCHAR);
    Field<String> script = field("State", SQLDataType.VARCHAR);
    Result<Record4<String, String, String, String>> result = CTX.newResult(type, version, description, script);
    migrationOutputList.forEach(output -> result.add(CTX.newRecord(type, version, description, script).values(
        String.format("%s %s", output.type, output.category),
        output.version,
        output.description,
        output.filepath)));
    return result.format();
  }

  /**
   * Format the {@link DatabaseMigrator#migrate()} output.
   */
  public static String format(MigrateResult result) {
    String output = String.format("Version: %s -> %s\n", result.initialSchemaVersion, result.targetSchemaVersion)
        + String.format("Migrations executed: %s\n", result.migrationsExecuted)
        + formatOutputs(result.migrations);
    return output;
  }

}
