/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.instance.BaseDatabaseMigrator;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevCenter;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.junit.Ignore;
import org.junit.jupiter.api.Test;

public class ConfigsDatabaseMigrationDevCenter extends AbstractConfigsDatabaseTest implements MigrationDevCenter {

  /**
   * 1. Run this method to create a new migration file.
   */
  @Ignore
  @Test
  @Override
  public void createMigration() throws IOException {
    BaseDatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigrationDevCenter.class.getSimpleName());
    MigrationDevHelper.createNextMigrationFile("configs", migrator);
  }

  /**
   * 2. Run this method to test the new migration.
   */
  @Ignore
  @Test
  @Override
  public void runLastMigration() throws IOException {
    BaseDatabaseMigrator fullMigrator = new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigrationDevCenter.class.getSimpleName());
    DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(fullMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
  }

  /**
   * 3. This method performs the following to integration the latest migration changes:
   * <li>Update the schema dump.</li>
   * <li>Update jOOQ-generated code.</li>
   *
   * Please make sure to check in the changes after running this method.
   */
  @Test
  @Override
  public void integrateMigration() throws Exception {
    DatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigrationDevCenter.class.getSimpleName());
    MigrationDevHelper.integrateMigration(container, migrator, "configs", ConfigsDatabaseMigrator.DB_SCHEMA_DUMP);
  }

}
