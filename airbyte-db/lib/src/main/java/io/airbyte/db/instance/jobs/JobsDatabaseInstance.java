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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseInstance;
import io.airbyte.db.instance.DatabaseInstance;
import java.io.IOException;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobsDatabaseInstance extends BaseDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobsDatabaseInstance.class);

  private static final String DATABASE_LOGGING_NAME = "airbyte jobs";
  private static final String SCHEMA_PATH = "jobs_database/schema.sql";
  private static final Function<Database, Boolean> IS_JOBS_DATABASE_READY = database -> {
    try {
      LOGGER.info("Testing if jobs database is ready...");
      return database.query(ctx -> JobsDatabaseSchema.getTableNames().stream().allMatch(table -> hasTable(ctx, table)));
    } catch (Exception e) {
      return false;
    }
  };

  @VisibleForTesting
  public JobsDatabaseInstance(String username, String password, String connectionString, String schema) {
    super(username, password, connectionString, schema, DATABASE_LOGGING_NAME, JobsDatabaseSchema.getTableNames(), IS_JOBS_DATABASE_READY);
  }

  public JobsDatabaseInstance(String username, String password, String connectionString) throws IOException {
    this(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH));
  }

}
