package io.airbyte.db.instance;

import java.io.IOException;
import java.util.List;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.BaselineResult;
import org.flywaydb.core.api.output.MigrateResult;

public interface DatabaseMigrator {

  /**
   * Run migration.
   */
  MigrateResult migrate();

  /**
   * List migration information.
   */
  List<MigrationInfo> info();

  /**
   * Create migration baseline.
   */
  BaselineResult baseline();

  /**
   * Dump the current database schema.
   */
  String dumpSchema() throws IOException;

  /**
   * Dump the current database schema to the default file.
   */
  String dumpSchemaToFile() throws IOException;

}
