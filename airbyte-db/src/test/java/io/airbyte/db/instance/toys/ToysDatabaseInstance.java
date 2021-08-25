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

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseInstance;
import java.io.IOException;
import java.util.Collections;
import java.util.function.Function;

/**
 * A database instance for testing purposes only.
 */
public class ToysDatabaseInstance extends BaseDatabaseInstance {

  public static final String DATABASE_LOGGING_NAME = "toys";
  public static final String TABLE_NAME = "toy_cars";
  public static final String SCHEMA_PATH = "toys_database/schema.sql";
  public static final Function<Database, Boolean> IS_DATABASE_READY = database -> {
    try {
      return database.query(ctx -> hasTable(ctx, TABLE_NAME));
    } catch (Exception e) {
      return false;
    }
  };

  protected ToysDatabaseInstance(String username, String password, String connectionString) throws IOException {
    super(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH), DATABASE_LOGGING_NAME, Collections.singleton(TABLE_NAME),
        IS_DATABASE_READY);
  }

}
