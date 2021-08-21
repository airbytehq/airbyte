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

package io.airbyte.db.instance.jobs;

import io.airbyte.db.instance.BaseDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.junit.Ignore;
import org.junit.jupiter.api.Test;

public class JobsDatabaseMigrationDevCenter extends AbstractJobsDatabaseTest {

  // 1. Run this method to create a new migration file.
  @Ignore
  @Test
  public void createMigration() throws IOException {
    BaseDatabaseMigrator migrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationDevCenter.class.getSimpleName());
    MigrationDevHelper.createNextMigrationFile("jobs", migrator);
  }

  // 2. Run this method to test the new migration.
  @Ignore
  @Test
  public void runLastMigration() throws IOException {
    BaseDatabaseMigrator fullMigrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationDevCenter.class.getSimpleName());
    DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(fullMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
  }

}
