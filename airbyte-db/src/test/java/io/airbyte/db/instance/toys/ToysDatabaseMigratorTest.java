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

package io.airbyte.db.instance.toys;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.instance.DatabaseMigrator;
import org.junit.jupiter.api.Test;

class ToysDatabaseMigratorTest extends AbstractToysDatabaseTest {

  /**
   * Apart from testing the migration, this method also generates a schema dump for the tests
   * database. The purpose is to ensure that the latest schema is checked into the codebase after all
   * migrations are executed.
   */
  @Test
  public void testMigration() throws Exception {
    DatabaseMigrator migrator = new ToysDatabaseMigrator(database, ToysDatabaseMigratorTest.class.getSimpleName());

    // Compare pre migration baseline schema
    migrator.baseline();
    String actualPreMigrationSchema = migrator.dumpSchema();
    String preMigrationSchema = MoreResources.readResource("toys_database/pre_migration_schema.txt").strip();
    assertEquals(preMigrationSchema, actualPreMigrationSchema, "The pre migration schema dump has changed");

    // Compare post migration schema
    migrator.migrate();
    String actualPostMigrationSchema = migrator.dumpSchemaToFile();
    String postMigrationSchema = MoreResources.readResource("toys_database/schema_dump.txt").strip();
    assertEquals(postMigrationSchema, actualPostMigrationSchema, "The post migration schema dump has changed");
  }

}
