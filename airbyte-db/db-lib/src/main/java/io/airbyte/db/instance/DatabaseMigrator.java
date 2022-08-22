/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

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
  List<MigrationInfo> list();

  /**
   * Get the latest migration information.
   */
  MigrationInfo getLatestMigration();

  /**
   * Setup Flyway migration in a database and create baseline.
   */
  BaselineResult createBaseline();

  /**
   * Dump the current database schema.
   */
  String dumpSchema() throws IOException;

}
